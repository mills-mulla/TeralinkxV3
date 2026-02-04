import { createStore } from 'vuex';
import axios from 'axios';

// Type definitions
interface Notification {
  id: number;
  content: string;
  [key: string]: any; // For any additional properties
}

interface AccountInfo {
  [key: string]: any; // Replace with actual account info structure
}

interface NotificationAction {
  type: string;
  payload?: any;
}

interface State {
  notifications: Notification[];
  notificationSocket: WebSocket | null;
  reconnectInterval: number;
  shouldReconnect: boolean;
  accountInfo: AccountInfo | null;
  dbChangeSocket: WebSocket | null;
  userId: string | null;
}

export default createStore<State>({
  state: {
    notifications: [],
    notificationSocket: null,
    reconnectInterval: 2000,
    shouldReconnect: true,
    accountInfo: null,
    dbChangeSocket: null,
    userId: localStorage.getItem('user_id') || null,
  },
  mutations: {
    addNotification(state: State, notification: Notification) {
      state.notifications.push(notification);
    },
    removeNotification(state: State, notificationId: number) {
      state.notifications = state.notifications.filter(
        notification => notification.id !== notificationId
      );
    },
    setNotificationSocket(state: State, socket: WebSocket | null) {
      state.notificationSocket = socket;
    },
    setShouldReconnect(state: State, shouldReconnect: boolean) {
      state.shouldReconnect = shouldReconnect;
    },
    setAccountInfo(state: State, accountInfo: AccountInfo) {
      state.accountInfo = accountInfo;
    },
  },
  actions: {
    setupWebSocket({ commit, state, dispatch }) {
      if (state.notificationSocket && state.notificationSocket.readyState === WebSocket.OPEN) {
        console.log("WebSocket is already open.");
        return;
      }

      const phone = localStorage.getItem("phone") || sessionStorage.getItem("phone");
      if (!phone) {
        console.error("Phone number not found in local storage or session storage");
        return;
      }

      const websocketProtocol = window.location.protocol === "https:" ? "wss" : "ws";
      const wsEndpoint = `${websocketProtocol}://127.0.0.1:8000/ws/notification/${phone}/`;

      const notificationSocket = new WebSocket(wsEndpoint);

      notificationSocket.onopen = () => {
        console.log("WebSocket connection opened for notifications!");
      };

      notificationSocket.onmessage = (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data);
          
          // Validate data structure and sanitize
          if (!data || typeof data !== 'object' || !data.message) {
            console.warn('Invalid message structure received');
            return;
          }
          
          const message = data.message;
          if (!message.message || typeof message.message !== 'string') {
            console.warn('Invalid message content received');
            return;
          }
          
          // Sanitize message content
          const messageContent = String(message.message).slice(0, 1000); // Limit length
          const notificationId = Date.now();
          
          // Only include safe properties
          const safeNotification = {
            content: messageContent,
            id: notificationId,
            timestamp: message.timestamp || new Date().toISOString()
          };
          
          commit('addNotification', safeNotification);

          // Validate action before processing
          if (message.action && typeof message.action === 'object' && 
              typeof message.action.type === 'string') {
            const allowedActions = ['RELOAD_PAGE', 'CLOSE_COMPONENT'];
            if (allowedActions.includes(message.action.type)) {
              dispatch('handleNotificationAction', message.action);
            }
          }

          setTimeout(() => {
            commit('removeNotification', notificationId);
          }, 10000);
        } catch (error) {
          if (error instanceof SyntaxError) {
            console.error("Invalid JSON received from WebSocket:", event.data);
          } else {
            console.error("Error processing WebSocket message:", error);
          }
          // Continue operation despite error
        }
      };

      notificationSocket.onclose = (event: CloseEvent) => {
        console.log("WebSocket connection closed for notifications!", event);
        commit('setNotificationSocket', null);

        if (state.shouldReconnect) {
          setTimeout(() => {
            dispatch('setupWebSocket');
          }, state.reconnectInterval);
        }
      };

      notificationSocket.onerror = (error: Event) => {
        console.error("WebSocket error for notifications: ", error);
        notificationSocket.close();
      };

      commit('setNotificationSocket', notificationSocket);
    },

    handleNotificationAction({ dispatch }, action: NotificationAction) {
      switch (action.type) {
        case 'RELOAD_PAGE':
          window.location.reload();
          break;
        case 'CLOSE_COMPONENT':
          dispatch('closeComponent', action.payload);
          break;
        default:
          console.warn(`Unknown action type: ${action.type}`);
      }
    },

    closeWebSocket({ commit, state }) {
      commit('setShouldReconnect', false);
      if (state.notificationSocket) {
        state.notificationSocket.close();
        commit('setNotificationSocket', null);
      }
      if (state.dbChangeSocket) {
        state.dbChangeSocket.close();
      }
    },

    async getAccountInfo({ commit }): Promise<AccountInfo> {
      const phoneNumber = localStorage.getItem('account');
      const sanitizedPhone = phoneNumber ? phoneNumber.replace(/[\r\n\t]/g, '') : null;
      console.log('Retrieved phone number from localStorage:', sanitizedPhone);

      if (!phoneNumber) {
        throw new Error('Phone number not found in local storage');
      }

      const requestData = JSON.stringify({ phone: phoneNumber });
      
      try {
        const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/getclient/`, requestData, {
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': localStorage.getItem('csrfToken') || '',
            Authorization: `Token ${localStorage.getItem('authToken')}`
          },
        });

        if (response.status === 200) {
          commit('setAccountInfo', response.data);
          return response.data;
        } else {
          throw new Error(`Unexpected response status: ${response.status}`);
        }
      } catch (error: any) {
        if (error.code === 'ECONNABORTED') {
          throw new Error('Request timeout. Please try again.');
        } else if (error.code === 'ERR_NETWORK') {
          throw new Error('Network error. Check your connection.');
        } else if (error.response?.status === 401) {
          throw new Error('Authentication failed. Please login again.');
        } else if (error.response?.status === 404) {
          throw new Error('Account not found.');
        } else if (error.response?.status >= 500) {
          throw new Error('Server error. Please try again later.');
        } else {
          console.error('Failed to retrieve account info:', error);
          throw new Error(error.response?.data?.message || 'Failed to retrieve account info');
        }
      }
    }
  },
  getters: {
    notifications: (state: State) => state.notifications,
    accountInfo: (state: State) => state.accountInfo,
  }
});