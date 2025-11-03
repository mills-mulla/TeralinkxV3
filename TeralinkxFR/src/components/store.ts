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
          if (data?.message?.message) {
            const messageContent = data.message.message;
            const notificationId = Date.now();
            commit('addNotification', { 
              content: messageContent, 
              id: notificationId,
              ...data.message // Include any additional data
            });

            if (data.message.action) {
              dispatch('handleNotificationAction', data.message.action);
            }

            setTimeout(() => {
              commit('removeNotification', notificationId);
            }, 10000);
          }
        } catch (error) {
          console.error("Error processing WebSocket message:", error);
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

    getAccountInfo({ commit }): Promise<AccountInfo> {
      return new Promise((resolve, reject) => {
        const phone_local = localStorage.getItem('account');
        console.log('Retrieved phone number from localStorage:', phone_local);

        if (!phone_local) {
          reject('Phone number not found in local storage');
          return;
        }

        const requestData = JSON.stringify({ phone: phone_local });
        
        axios.post(`${import.meta.env.VITE_API_BASE_URL}/api/getclient/`, requestData, {
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': localStorage.getItem('csrfToken') || '',
            Authorization: `Token ${localStorage.getItem('authToken')}`
          },
        })
        .then((response) => {
          if (response.status === 200) {
            commit('setAccountInfo', response.data);
            resolve(response.data);
          } else {
            reject('Unexpected response from server');
          }
        })
        .catch((error) => {
          console.error('Failed to retrieve account info:', error);
          reject(error);
        });
      });
    }
  },
  getters: {
    notifications: (state: State) => state.notifications,
    accountInfo: (state: State) => state.accountInfo,
  }
});