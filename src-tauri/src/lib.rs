use std::sync::Mutex;
use std::process::{Child, Command};
use tauri::State;

// State to manage the active playback child process (afplay or say)
#[derive(Default)]
pub struct VoiceState {
    player_process: Mutex<Option<Child>>,
}

// Clean markdown and formatting tags from TTS text
fn clean_text(text: &str) -> String {
    let mut cleaned = text.to_string();
    cleaned = cleaned.replace("**", "");
    cleaned = cleaned.replace("*", "");
    cleaned = cleaned.replace("`", "");
    cleaned = cleaned.replace("#", "");
    cleaned = cleaned.replace("---", " ");
    cleaned = cleaned.replace("═══", " ");
    cleaned = cleaned.replace("\n", ". ");
    cleaned = cleaned.replace("  ", " ");
    cleaned.chars().take(700).collect()
}

// 1. Chat command linking to the n8n holding brain chatbot webhook
#[tauri::command]
async fn chat_n8n(message: String) -> Result<String, String> {
    let client = reqwest::Client::new();
    let url = "https://aherreras.app.n8n.cloud/webhook/mila-holding-brain/chat";
    
    let res = client.post(url)
        .json(&serde_json::json!({
            "chatInput": message,
            "sessionId": "mila-voice-local-app"
        }))
        .send()
        .await
        .map_err(|e| format!("n8n Connection Error: {}", e))?;

    let json: serde_json::Value = res.json().await
        .map_err(|e| format!("JSON parse error: {}", e))?;
    
    let reply = json.get("output")
        .or_else(|| json.get("text"))
        .or_else(|| json.get("message"))
        .and_then(|v| v.as_str())
        .unwrap_or("Non ho capito, puoi ripetere?");

    Ok(reply.to_string())
}

// Helper to kill currently playing processes
fn stop_tts_internal(state: &VoiceState) {
    let mut player = state.player_process.lock().unwrap();
    if let Some(mut child) = player.take() {
        let _ = child.kill();
    }
    // Defensive cleanup for macOS system speech
    let _ = Command::new("pkill").args(&["-f", "say"]).output();
}

// 2. TTS Voice generation command
#[tauri::command]
async fn speak_tts(state: State<'_, VoiceState>, text: String) -> Result<(), String> {
    // Stop any speech currently playing
    stop_tts_internal(&state);

    let cleaned = clean_text(&text);
    if cleaned.is_empty() {
        return Ok(());
    }

    // Attempt ElevenLabs TTS (La Sapa Voice ID)
    let client = reqwest::Client::new();
    let elevenlabs_url = "https://api.elevenlabs.io/v1/text-to-speech/TgSKipUvZrUHVPv7imoO";
    let api_key = "sk_6850414ef429e3c774d739434599ee66d2f04850182e9e0a";

    let res = client.post(elevenlabs_url)
        .header("xi-api-key", api_key)
        .header("Content-Type", "application/json")
        .header("Accept", "audio/mpeg")
        .json(&serde_json::json!({
            "text": cleaned,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.60,
                "similarity_boost": 0.85
            },
            "speed": 1.5
        }))
        .send()
        .await;

    match res {
        Ok(response) if response.status().is_success() => {
            if let Ok(bytes) = response.bytes().await {
                let temp_path = "/tmp/mila_eleven.mp3";
                if std::fs::write(temp_path, bytes).is_ok() {
                    // Play using macOS native afplay command
                    if let Ok(child) = Command::new("afplay").arg(temp_path).spawn() {
                        let mut player = state.player_process.lock().unwrap();
                        *player = Some(child);
                        return Ok(());
                    }
                }
            }
        }
        _ => {} // Fallback on failure
    }

    // Fallback: macOS local TTS using "Alice" (Italian natural voice)
    if let Ok(child) = Command::new("say")
        .args(&["-v", "Alice", "-r", "243", &cleaned])
        .spawn()
    {
        let mut player = state.player_process.lock().unwrap();
        *player = Some(child);
        Ok(())
    } else {
        Err("Failed to play text-to-speech".to_string())
    }
}

// 3. Stop speaking command
#[tauri::command]
fn stop_tts(state: State<'_, VoiceState>) -> Result<(), String> {
    stop_tts_internal(&state);
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .manage(VoiceState::default())
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![chat_n8n, speak_tts, stop_tts])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
