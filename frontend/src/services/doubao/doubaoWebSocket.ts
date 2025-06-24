/**
 * Doubao WebSocket Service
 * 豆包WebSocket服务 - [services][doubao][websocket]
 */

import { message } from 'antd';

interface WebSocketConfig {
  url: string;
  protocols?: string | string[];
  reconnectAttempts?: number;
  reconnectInterval?: number;
}

interface TTSStreamData {
  text: string;
  voice_type: string;
  encoding?: string;
  speed_ratio?: number;
  volume_ratio?: number;
  pitch_ratio?: number;
  sample_rate?: number;
  [key: string]: any;
}

interface StreamCallbacks {
  onChunk?: (chunk: Uint8Array) => void;
  onComplete?: (audioData: Uint8Array) => void;
  onError?: (error: Error) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
}

/**
 * 豆包WebSocket服务类
 * [services][doubao][websocket][DoubaoWebSocketService]
 */
export class DoubaoWebSocketService {
  private ws: WebSocket | null = null;
  private config: WebSocketConfig;
  private callbacks: StreamCallbacks = {};
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 3;
  private reconnectInterval = 3000;
  private audioChunks: Uint8Array[] = [];
  private isConnecting = false;
  private isManuallyDisconnected = false;

  constructor(config: WebSocketConfig) {
    this.config = config;
    this.maxReconnectAttempts = config.reconnectAttempts || 3;
    this.reconnectInterval = config.reconnectInterval || 3000;
  }

  /**
   * 连接WebSocket
   * [services][doubao][websocket][connect]
   */
  async connect(): Promise<void> {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      return Promise.resolve();
    }

    this.isConnecting = true;
    this.isManuallyDisconnected = false;

    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.config.url, this.config.protocols);
        
        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          
          if (this.callbacks.onConnect) {
            this.callbacks.onConnect();
          }
          
          resolve();
        };

        this.ws.onmessage = (event) => {
          this.handleMessage(event);
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.isConnecting = false;
          
          const wsError = new Error('WebSocket连接错误');
          if (this.callbacks.onError) {
            this.callbacks.onError(wsError);
          }
          
          reject(wsError);
        };

        this.ws.onclose = (event) => {
          console.log('WebSocket closed:', event.code, event.reason);
          this.isConnecting = false;
          
          if (this.callbacks.onDisconnect) {
            this.callbacks.onDisconnect();
          }

          // 自动重连（如果不是手动断开）
          if (!this.isManuallyDisconnected && this.shouldReconnect()) {
            this.attemptReconnect();
          }
        };

      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  /**
   * 处理WebSocket消息
   * [services][doubao][websocket][handleMessage]
   */
  private handleMessage(event: MessageEvent): void {
    try {
      if (event.data instanceof ArrayBuffer) {
        // 二进制音频数据
        const audioChunk = new Uint8Array(event.data);
        this.audioChunks.push(audioChunk);
        
        if (this.callbacks.onChunk) {
          this.callbacks.onChunk(audioChunk);
        }
      } else if (typeof event.data === 'string') {
        // JSON控制消息
        const message = JSON.parse(event.data);
        
        if (message.type === 'complete') {
          // 合成完成
          const completeAudio = this.mergeAudioChunks();
          if (this.callbacks.onComplete) {
            this.callbacks.onComplete(completeAudio);
          }
          this.audioChunks = []; // 清空缓存
        } else if (message.type === 'error') {
          // 错误消息
          const error = new Error(message.error || '流式合成错误');
          if (this.callbacks.onError) {
            this.callbacks.onError(error);
          }
        }
      }
    } catch (error) {
      console.error('Message handling error:', error);
      if (this.callbacks.onError) {
        this.callbacks.onError(error as Error);
      }
    }
  }

  /**
   * 合并音频数据块
   * [services][doubao][websocket][mergeAudioChunks]
   */
  private mergeAudioChunks(): Uint8Array {
    const totalLength = this.audioChunks.reduce((sum, chunk) => sum + chunk.length, 0);
    const mergedArray = new Uint8Array(totalLength);
    
    let offset = 0;
    this.audioChunks.forEach(chunk => {
      mergedArray.set(chunk, offset);
      offset += chunk.length;
    });
    
    return mergedArray;
  }

  /**
   * 发送TTS流式请求
   * [services][doubao][websocket][streamTTS]
   */
  async streamTTS(data: TTSStreamData, callbacks: StreamCallbacks): Promise<void> {
    this.callbacks = callbacks;
    this.audioChunks = []; // 重置音频缓存

    try {
      // 确保连接已建立
      await this.connect();

      if (this.ws?.readyState !== WebSocket.OPEN) {
        throw new Error('WebSocket未连接');
      }

      // 发送TTS请求
      const request = {
        type: 'tts_request',
        data: {
          ...data,
          text: data.text,
          voice_type: data.voice_type,
          encoding: data.encoding || 'mp3',
          speed_ratio: data.speed_ratio || 1.0,
          volume_ratio: data.volume_ratio || 1.0,
          pitch_ratio: data.pitch_ratio || 1.0,
          sample_rate: data.sample_rate || 24000
        }
      };

      this.ws.send(JSON.stringify(request));
      console.log('TTS request sent:', request);

    } catch (error) {
      console.error('Stream TTS error:', error);
      if (this.callbacks.onError) {
        this.callbacks.onError(error as Error);
      }
      throw error;
    }
  }

  /**
   * 判断是否应该重连
   * [services][doubao][websocket][shouldReconnect]
   */
  private shouldReconnect(): boolean {
    return this.reconnectAttempts < this.maxReconnectAttempts;
  }

  /**
   * 尝试重连
   * [services][doubao][websocket][attemptReconnect]
   */
  private attemptReconnect(): void {
    this.reconnectAttempts++;
    
    console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
    
    setTimeout(() => {
      this.connect().catch(error => {
        console.error('Reconnection failed:', error);
        
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
          message.error('WebSocket重连失败，请刷新页面重试');
          if (this.callbacks.onError) {
            this.callbacks.onError(new Error('WebSocket重连失败'));
          }
        }
      });
    }, this.reconnectInterval);
  }

  /**
   * 断开连接
   * [services][doubao][websocket][disconnect]
   */
  disconnect(): void {
    this.isManuallyDisconnected = true;
    
    if (this.ws) {
      this.ws.close(1000, 'Manual disconnect');
      this.ws = null;
    }
    
    this.audioChunks = [];
    this.callbacks = {};
  }

  /**
   * 获取连接状态
   * [services][doubao][websocket][getReadyState]
   */
  getReadyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }

  /**
   * 是否已连接
   * [services][doubao][websocket][isConnected]
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * 设置回调函数
   * [services][doubao][websocket][setCallbacks]
   */
  setCallbacks(callbacks: StreamCallbacks): void {
    this.callbacks = { ...this.callbacks, ...callbacks };
  }

  /**
   * 清除回调函数
   * [services][doubao][websocket][clearCallbacks]
   */
  clearCallbacks(): void {
    this.callbacks = {};
  }
}

// 导出默认WebSocket服务实例
let defaultWebSocketService: DoubaoWebSocketService | null = null;

/**
 * 获取默认WebSocket服务实例
 * [services][doubao][websocket][getDefaultService]
 */
export const getDefaultWebSocketService = (): DoubaoWebSocketService => {
  if (!defaultWebSocketService) {
    // 从环境变量或配置中获取WebSocket URL
    const wsUrl = process.env.VITE_WS_URL || 'ws://localhost:8000/api/v1/doubao/voice/tts/ws';
    
    defaultWebSocketService = new DoubaoWebSocketService({
      url: wsUrl,
      reconnectAttempts: 3,
      reconnectInterval: 3000
    });
  }
  
  return defaultWebSocketService;
};

/**
 * 清理默认WebSocket服务
 * [services][doubao][websocket][cleanup]
 */
export const cleanupDefaultWebSocketService = (): void => {
  if (defaultWebSocketService) {
    defaultWebSocketService.disconnect();
    defaultWebSocketService = null;
  }
};