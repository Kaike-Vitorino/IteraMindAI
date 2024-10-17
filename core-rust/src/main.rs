use serde::{Deserialize, Serialize};
use std::error::Error;

#[derive(Serialize, Deserialize, Debug)]
struct Task {
    description: String,
    subtasks: Vec<String>,
}

fn main() -> Result<(), Box<dyn Error>> {
    let task = Task {
        description: "Main task".to_string(),
        subtasks: vec![
            "Subtask 1".to_string(),
            "Subtask 2".to_string(),
            "Subtask 3".to_string(),
        ],
    };

    let serialized = serde_json::to_string(&task)?;
    println!("Serialized Task: {}", serialized);

    Ok(())
}
