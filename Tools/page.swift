// Saves a picture of one slide, to check the design without installing the screensaver.
//   swift Tools/page.swift web/index.html "q=2&side=a" out.png [width] [height]
import AppKit
import WebKit

let a = CommandLine.arguments
let w = a.count > 4 ? Double(a[4])! : 1920, h = a.count > 5 ? Double(a[5])! : 1080
let file = URL(fileURLWithPath: a[1]).absoluteURL
var parts = URLComponents(url: file, resolvingAgainstBaseURL: true)!
parts.query = a[2]
let app = NSApplication.shared
app.setActivationPolicy(.accessory)
let web = WKWebView(frame: NSRect(x: 0, y: 0, width: w, height: h))
let win = NSWindow(contentRect: web.frame, styleMask: [.borderless], backing: .buffered, defer: false)
win.contentView = web
win.setFrameOrigin(NSPoint(x: -10000, y: -10000))
win.orderFront(nil)
web.loadFileURL(parts.url!, allowingReadAccessTo: file.deletingLastPathComponent())
DispatchQueue.main.asyncAfter(deadline: .now() + 2.5) {
    web.takeSnapshot(with: nil) { img, _ in
        guard let t = img?.tiffRepresentation, let png = NSBitmapImageRep(data: t)?.representation(using: .png, properties: [:]) else { print("no picture"); exit(1) }
        try! png.write(to: URL(fileURLWithPath: a[3]))
        exit(0)
    }
}
app.run()
