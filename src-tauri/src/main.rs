#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use std::fs::File;
use std::io::{BufReader, BufWriter};
use std::net::UdpSocket;
use std::str::FromStr;
use tauri::Manager;

const HOSTPORT: &str = "127.0.0.1:12345";
const SCORE_FILE: &str = ".dino_score";

#[tauri::command]
fn get_high_score() -> u64 {
    let old_score: u64 = match File::open(SCORE_FILE) {
        Ok(f) => serde_json::from_reader(BufReader::new(f)).expect("Could not deserialize score!"),
        Err(_) => 0,
    };

    println!("Loaded high score: {:?}", old_score);
    old_score
}

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            app.listen_global("saveHighScore", |event| {
                if let Some(payload) = event.payload() {
                    if let Ok(f) = File::create(SCORE_FILE) {
                        if serde_json::to_writer(
                            BufWriter::new(f),
                            &u64::from_str(payload).unwrap(),
                        )
                        .is_err()
                        {
                            println!(" Failed to save score!");
                        }
                    }
                }
                println!("Saving high score: {:?}", event.payload());
            });
            jump(app.get_window("main").unwrap());
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![get_high_score])
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
                let parsed: &str = std::str::from_utf8(&buf[..1]).unwrap().trim();
                println!("Received: {}", parsed);
                window.emit(parsed, ()).unwrap();
            }
            Err(e) => {
                println!("{}", e);
            }
        }
    });
}
