// [Task]: T078 [From]: plan.md §Phase C, contracts/api-extensions.yaml §WebSocket
/**
 * WebSocket client library.
 * Connects to the backend WebSocket endpoint for real-time updates.
 * Supports auto-reconnect with exponential backoff.
 */

export type WebSocketMessageType = "task_update" | "reminder";

export interface WebSocketMessage {
  type: WebSocketMessageType;
  payload: Record<string, unknown>;
}

export type MessageHandler = (message: WebSocketMessage) => void;

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class TodoWebSocket {
  private ws: WebSocket | null = null;
  private userId: string;
  private handlers: Set<MessageHandler> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private _closed = false;

  constructor(userId: string) {
    this.userId = userId;
  }

  /**
   * Connect to the WebSocket endpoint.
   */
  connect(): void {
    if (this._closed) return;

    const wsUrl = API_URL.replace(/^http/, "ws") + `/api/ws/${this.userId}`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log("[WS] Connected to", wsUrl);
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.handlers.forEach((handler) => handler(message));
        } catch {
          console.warn("[WS] Failed to parse message:", event.data);
        }
      };

      this.ws.onclose = (event) => {
        console.log("[WS] Disconnected:", event.code, event.reason);
        if (!this._closed) {
          this.scheduleReconnect();
        }
      };

      this.ws.onerror = () => {
        console.warn("[WS] Connection error");
      };
    } catch {
      console.warn("[WS] Failed to create WebSocket");
      this.scheduleReconnect();
    }
  }

  /**
   * Register a message handler.
   */
  onMessage(handler: MessageHandler): () => void {
    this.handlers.add(handler);
    return () => this.handlers.delete(handler);
  }

  /**
   * Close the connection permanently.
   */
  close(): void {
    this._closed = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
    this.ws?.close();
    this.ws = null;
    this.handlers.clear();
  }

  /**
   * Schedule a reconnection attempt with exponential backoff.
   */
  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.warn("[WS] Max reconnect attempts reached");
      return;
    }

    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
    this.reconnectAttempts++;

    console.log(`[WS] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
    this.reconnectTimer = setTimeout(() => this.connect(), delay);
  }

  /**
   * Check if the connection is open.
   */
  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}
