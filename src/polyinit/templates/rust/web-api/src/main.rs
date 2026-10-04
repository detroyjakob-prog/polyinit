use axum::{routing::get, Json, Router};
use serde::Serialize;

#[derive(Serialize)]
struct Message {
    message: String,
}

#[derive(Serialize)]
struct Status {
    status: String,
}

async fn root() -> Json<Message> {
    Json(Message {
        message: "Hello from {{project_name}}!".to_string(),
    })
}

async fn healthz() -> Json<Status> {
    Json(Status {
        status: "ok".to_string(),
    })
}

#[tokio::main]
async fn main() {
    let app = Router::new().route("/", get(root)).route("/healthz", get(healthz));

    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000")
        .await
        .expect("Failed to bind port");
    println!("Listening on http://127.0.0.1:3000");
    axum::serve(listener, app).await.expect("Server failed");
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(1 + 1, 2);
    }
}