#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use tauri::Manager;

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            jump(app.get_window("main").unwrap());
            Ok(())
        })
        .on_page_load(|app, _ev| {})
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

fn jump(window: tauri::Window) {
    std::thread::spawn(move || loop {
        std::thread::sleep(std::time::Duration::from_secs(1));
        window.emit("jump", {}).unwrap();
    });
}
