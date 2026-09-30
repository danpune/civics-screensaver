// Makes one video from a plan written by make_videos.py.
//   swift Tools/video.swift web/index.html plan.json out.mp4 [thumbnail.jpg]
// The plan lists the slides in order: {"q": 12, "side": "q", "sec": 5} or {"card": {"k", "h", "lines"}, "sec": 8}.
// 1920x1080, 30 frames a second, H.264, with AAC sound when the plan says "sound": true.
// The background sound is made here from sine waves and soft noise, so it has no owner and needs no licence.
// Needs nothing but macOS.
import AppKit
import WebKit
import AVFoundation

let arg = CommandLine.arguments
guard arg.count == 4 || arg.count == 5 else { print("usage: video <index.html> <plan.json> <out.mp4> [thumbnail.jpg]"); exit(1) }
let page = URL(fileURLWithPath: arg[1]).absoluteURL, out = URL(fileURLWithPath: arg[3])
struct Card: Codable { let k: String; let h: String; let lines: [String] }
struct Slide: Codable { let q: Int?; let side: String?; let card: Card?; let sec: Double }
struct Plan: Codable { let slides: [Slide]; let sound: Bool }
let plan = try! JSONDecoder().decode(Plan.self, from: Data(contentsOf: URL(fileURLWithPath: arg[2])))

let W = 1920, H = 1080, FPS: Int32 = 30, FADE = 12   // FADE: frames of cross-fade between two slides
let GOLD = CGColor(red: 0.94, green: 0.78, blue: 0.40, alpha: 0.8)
func fail(_ s: String) -> Never { print(s); exit(1) }

func buffer(_ draw: (CGContext) -> Void) -> CVPixelBuffer {
    var pb: CVPixelBuffer?
    CVPixelBufferCreate(nil, W, H, kCVPixelFormatType_32ARGB, [kCVPixelBufferCGImageCompatibilityKey: true, kCVPixelBufferCGBitmapContextCompatibilityKey: true] as CFDictionary, &pb)
    guard let b = pb else { fail("no pixel buffer") }
    CVPixelBufferLockBaseAddress(b, [])
    let c = CGContext(data: CVPixelBufferGetBaseAddress(b), width: W, height: H, bitsPerComponent: 8, bytesPerRow: CVPixelBufferGetBytesPerRow(b),
                      space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue)!
    c.interpolationQuality = .high
    draw(c)
    CVPixelBufferUnlockBaseAddress(b, [])
    return b
}
let full = CGRect(x: 0, y: 0, width: W, height: H)

// A quiet, slow chord over soft noise, faded in and out.
func writeSound(seconds: Double, to url: URL) throws {
    let rate = 44100.0, n = Int(seconds * rate)
    let fmt = AVAudioFormat(standardFormatWithSampleRate: rate, channels: 2)!
    let file = try AVAudioFile(forWriting: url, settings: [AVFormatIDKey: kAudioFormatMPEG4AAC, AVSampleRateKey: rate, AVNumberOfChannelsKey: 2, AVEncoderBitRateKey: 128000])
    let notes: [Double] = [110.00, 164.81, 220.00, 277.18, 329.63]          // A major, low and wide
    let swell: [Double] = [0.031, 0.043, 0.057, 0.071, 0.089]               // each note rises and falls at its own pace
    var seed: UInt64 = 20260929, brownL = 0.0, brownR = 0.0
    func noise() -> Double { seed = seed &* 6364136223846793005 &+ 1442695040888963407; return Double(seed >> 33) / Double(1 << 30) - 1 }
    var done = 0
    while done < n {
        let count = min(44100, n - done)
        let buf = AVAudioPCMBuffer(pcmFormat: fmt, frameCapacity: AVAudioFrameCount(count))!
        buf.frameLength = AVAudioFrameCount(count)
        let L = buf.floatChannelData![0], R = buf.floatChannelData![1]
        for i in 0..<count {
            let t = Double(done + i) / rate
            var l = 0.0, r = 0.0
            for k in 0..<notes.count {
                let gain = 0.5 + 0.5 * sin(2 * .pi * swell[k] * t + Double(k) * 1.3)
                l += gain * sin(2 * .pi * (notes[k] - 0.12) * t)
                r += gain * sin(2 * .pi * (notes[k] + 0.12) * t + 0.4)
            }
            brownL = (brownL + 0.02 * noise()) * 0.998
            brownR = (brownR + 0.02 * noise()) * 0.998
            let edge = max(0, min(1, t / 3, (seconds - t) / 4))               // fade in over 3 seconds, out over 4
            L[i] = Float((0.030 * l + 0.10 * brownL) * edge)
            R[i] = Float((0.030 * r + 0.10 * brownR) * edge)
        }
        try file.write(from: buf)
        done += count
    }
}

let app = NSApplication.shared
app.setActivationPolicy(.accessory)
let web = WKWebView(frame: NSRect(x: 0, y: 0, width: W, height: H))
let win = NSWindow(contentRect: web.frame, styleMask: [.borderless], backing: .buffered, defer: false)
win.contentView = web
win.setFrameOrigin(NSPoint(x: -10000, y: -10000))
win.orderFront(nil)
var parts = URLComponents(url: page, resolvingAgainstBaseURL: true)!
parts.query = "video=1"
web.loadFileURL(parts.url!, allowingReadAccessTo: page.deletingLastPathComponent())

@MainActor func js(_ s: String) async -> Any? { try? await web.evaluateJavaScript(s) }
@MainActor func shot(_ s: Slide) async -> CGImage {
    var call = ""
    if let c = s.card { call = "card(\(String(data: try! JSONEncoder().encode(c), encoding: .utf8)!))" }
    else if let q = s.q { call = "pin(\(q), '\(s.side == "a" ? "a" : "q")')" }
    var state = await js(call) as? String
    for _ in 0..<100 where state != "ready" {
        try? await Task.sleep(nanoseconds: 50_000_000)
        state = (await js("(function(){ var i = document.querySelector('.slide img'); return !i || (i.complete && i.naturalWidth > 0) ? 'ready' : 'wait'; })()")) as? String
    }
    guard state == "ready" else { fail("slide not ready: \(call)") }
    try? await Task.sleep(nanoseconds: 150_000_000)   // the slide is fitted again once the picture has its size
    let cfg = WKSnapshotConfiguration()
    cfg.snapshotWidth = NSNumber(value: W)
    guard let img = try? await web.takeSnapshot(configuration: cfg), let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { fail("no picture of \(call)") }
    return cg
}

Task { @MainActor in
    for _ in 0..<100 { if (await js("typeof card")) as? String == "function" { break }; try? await Task.sleep(nanoseconds: 100_000_000) }
    guard (await js("typeof card")) as? String == "function" else { fail("the page did not load in video mode") }

    let silent = out.deletingPathExtension().appendingPathExtension("silent.mp4"), m4a = out.deletingPathExtension().appendingPathExtension("m4a")
    for u in [silent, m4a, out] { try? FileManager.default.removeItem(at: u) }
    let writer = try! AVAssetWriter(outputURL: silent, fileType: .mp4)
    let input = AVAssetWriterInput(mediaType: .video, outputSettings: [AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: W, AVVideoHeightKey: H,
        AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: 6_000_000, AVVideoMaxKeyFrameIntervalKey: 60, AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel]])
    let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: nil)
    writer.add(input)
    guard writer.startWriting() else { fail("cannot write: \(String(describing: writer.error))") }
    writer.startSession(atSourceTime: .zero)

    var frame: Int64 = 0
    func put(_ b: CVPixelBuffer) async {
        while !input.isReadyForMoreMediaData { try? await Task.sleep(nanoseconds: 2_000_000) }
        if !adaptor.append(b, withPresentationTime: CMTime(value: frame, timescale: FPS)) { fail("frame \(frame): \(String(describing: writer.error))") }
        frame += 1
    }
    var before: CGImage? = nil
    for (n, s) in plan.slides.enumerated() {
        let now = await shot(s)
        let frames = Int((s.sec * Double(FPS)).rounded())
        let fade = before == nil ? 0 : min(FADE, frames)
        for k in 0..<fade {
            await put(buffer { c in c.draw(before!, in: full); c.setAlpha(CGFloat(k + 1) / CGFloat(FADE + 1)); c.draw(now, in: full) })
        }
        if s.q != nil && s.side != "a" {
            // a question: a thin gold line fills the bottom edge while the viewer thinks of the answer
            for k in fade..<frames {
                await put(buffer { c in c.draw(now, in: full); c.setFillColor(GOLD); c.fill(CGRect(x: 0, y: 0, width: Double(W) * Double(k + 1) / Double(frames), height: 6)) })
            }
        } else {
            let still = buffer { $0.draw(now, in: full) }
            for _ in fade..<frames { await put(still) }
        }
        if n == 0 && arg.count == 5 {   // the title card, 1280x720, for the video's thumbnail
            let small = NSImage(size: NSSize(width: 1280, height: 720))
            small.lockFocus(); NSGraphicsContext.current?.imageInterpolation = .high
            NSImage(cgImage: now, size: .zero).draw(in: NSRect(x: 0, y: 0, width: 1280, height: 720)); small.unlockFocus()
            let rep = NSBitmapImageRep(data: small.tiffRepresentation!)!
            try! rep.representation(using: .jpeg, properties: [.compressionFactor: 0.9])!.write(to: URL(fileURLWithPath: arg[4]))
        }
        before = now
        if n % 25 == 0 { print("slide \(n + 1) of \(plan.slides.count)") }
    }
    input.markAsFinished()
    await writer.finishWriting()
    guard writer.status == .completed else { fail("video not written: \(String(describing: writer.error))") }
    let seconds = Double(frame) / Double(FPS)

    if !plan.sound { try! FileManager.default.moveItem(at: silent, to: out); print("wrote \(out.lastPathComponent): \(Int(seconds)) seconds, no sound"); exit(0) }
    try! writeSound(seconds: seconds, to: m4a)
    let mix = AVMutableComposition()
    let span = CMTimeRange(start: .zero, duration: CMTime(value: frame, timescale: FPS))
    try! mix.addMutableTrack(withMediaType: .video, preferredTrackID: kCMPersistentTrackID_Invalid)!.insertTimeRange(span, of: try! await AVURLAsset(url: silent).loadTracks(withMediaType: .video)[0], at: .zero)
    try! mix.addMutableTrack(withMediaType: .audio, preferredTrackID: kCMPersistentTrackID_Invalid)!.insertTimeRange(span, of: try! await AVURLAsset(url: m4a).loadTracks(withMediaType: .audio)[0], at: .zero)
    guard let ex = AVAssetExportSession(asset: mix, presetName: AVAssetExportPresetPassthrough) else { fail("cannot join sound and picture") }
    do { try await ex.export(to: out, as: .mp4) } catch { fail("not joined: \(error)") }
    for u in [silent, m4a] { try? FileManager.default.removeItem(at: u) }
    print("wrote \(out.lastPathComponent): \(Int(seconds)) seconds")
    exit(0)
}
app.run()
