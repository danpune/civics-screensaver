// Loads the built screensaver, runs it in a small window and saves what it shows as PNG files.
//   swift Tools/shot.swift "build/Civics Test.saver" out [seconds ...]
// One picture is saved for each number of seconds given, as out-<seconds>.png.
import AppKit
import ScreenSaver
import WebKit

let a = CommandLine.arguments
let times = a.dropFirst(3).compactMap { Double($0) }
guard let b = Bundle(path: a[1]), b.load(), let cls = b.principalClass as? ScreenSaverView.Type,
      let v = cls.init(frame: NSRect(x: 0, y: 0, width: 960, height: 540), isPreview: false) else { print("could not load the screensaver"); exit(1) }
let app = NSApplication.shared
app.setActivationPolicy(.accessory)
let win = NSWindow(contentRect: v.frame, styleMask: [.borderless], backing: .buffered, defer: false)
win.contentView = v
win.setFrameOrigin(NSPoint(x: 40, y: 40))   // on screen: a hidden web page does not run its fades
win.level = .floating
win.orderFrontRegardless()
v.startAnimation()
for t in times {
    DispatchQueue.main.asyncAfter(deadline: .now() + t) {
        guard let web = v.subviews.compactMap({ $0 as? WKWebView }).first else { print("no web view"); exit(1) }
        web.takeSnapshot(with: nil) { img, err in
            guard let tiff = img?.tiffRepresentation, let png = NSBitmapImageRep(data: tiff)?.representation(using: .png, properties: [:]) else { print("no picture: \(String(describing: err))"); exit(1) }
            try! png.write(to: URL(fileURLWithPath: "\(a[2])-\(Int(t)).png"))
            print("saved \(a[2])-\(Int(t)).png")
            if t == times.last { v.stopAnimation(); exit(0) }
        }
    }
}
app.run()
