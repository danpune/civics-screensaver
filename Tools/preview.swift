// Shows the built screensaver full screen, without changing any setting.
//   swift Tools/preview.swift "build/Civics Test.saver" [seconds]
// Press any key or click to close it. It closes by itself after the given number of seconds (default 60).
import AppKit
import ScreenSaver

let a = CommandLine.arguments
let limit = a.count > 2 ? Double(a[2]) ?? 60 : 60
guard let screen = NSScreen.main, let b = Bundle(path: a[1]), b.load(), let cls = b.principalClass as? ScreenSaverView.Type,
      let v = cls.init(frame: NSRect(origin: .zero, size: screen.frame.size), isPreview: false) else { print("could not load the screensaver"); exit(1) }

final class Win: NSWindow {
    override var canBecomeKey: Bool { true }
    override func keyDown(with e: NSEvent) { exit(0) }
    override func mouseDown(with e: NSEvent) { exit(0) }
}
let app = NSApplication.shared
app.setActivationPolicy(.regular)
let win = Win(contentRect: screen.frame, styleMask: [.borderless], backing: .buffered, defer: false)
win.level = .screenSaver
win.backgroundColor = .black
win.contentView = v
win.makeKeyAndOrderFront(nil)
app.activate(ignoringOtherApps: true)
NSCursor.hide()
v.startAnimation()
DispatchQueue.main.asyncAfter(deadline: .now() + limit) { exit(0) }
app.run()
