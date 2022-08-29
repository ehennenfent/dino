#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use std::net::UdpSocket;
use tauri::Manager;

const HOSTPORT: &str = "127.0.0.1:12345";

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            jump(app.get_window("main").unwrap());
            Ok(())
        })
        .on_page_load(|_app, _ev| {})
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

fn jump(window: tauri::Window) {
    let socket = UdpSocket::bind(HOSTPORT).expect("Could not bind to socket");
    socket
        .set_read_timeout(None)
        .expect("set_read_timeout call failed");

    let mut buf = [0; 2];

    std::thread::spawn(move || loop {
        match socket.recv_from(&mut buf) {
            Ok((_amt, _src)) => {
                let parsed: &str = std::str::from_utf8(&buf).unwrap().trim();
                println!("Received: {}", parsed);
                window.emit(parsed, {}).unwrap();
            }
            Err(e) => {
                println!("{}", e);
            }
        }
    });
}
