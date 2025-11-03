<template>
    <div>
      <h1>Local IP Address</h1>
      <p v-if="localIP">{{ localIP }}</p>
      <p v-else>Loading local IP...</p>
    </div>
  </template>
  
  <script>
  export default {
    name: "LocalIP",
    data() {
      return {
        localIP: ''
      };
    },
    mounted() {
      this.getLocalIP()
        .then((ip) => {
          this.localIP = ip;
        })
        .catch((error) => {
          this.localIP = `Error: ${error}`;
        });
    },
    methods: {
      getLocalIP() {
        return new Promise((resolve, reject) => {
          let ipFound = false;
          const pc = new RTCPeerConnection({ iceServers: [] });
          // Create a dummy data channel to trigger ICE candidate gathering.
          pc.createDataChannel('');
          pc.createOffer()
            .then((offer) => pc.setLocalDescription(offer))
            .catch(reject);
  
          // Listen for ICE candidates
          pc.onicecandidate = (event) => {
            if (event && event.candidate && event.candidate.candidate) {
              const candidate = event.candidate.candidate;
              // Regular expression to extract an IPv4 address.
              const ipRegex = /([0-9]{1,3}\.){3}[0-9]{1,3}/;
              const ipMatch = candidate.match(ipRegex);
              if (ipMatch && !ipFound) {
                ipFound = true;
                resolve(ipMatch[0]);
                pc.close(); // Clean up the connection.
              }
            }
          };
  
          // Set a timeout to reject if no IP is found.
          setTimeout(() => {
            if (!ipFound) {
              reject('Could not find local IP');
            }
          }, 3000);
        });
      }
    }
  };
  </script>
  
  <style scoped>
  h1 {
    font-family: Arial, sans-serif;
    color: #333;
  }
  p {
    font-family: Arial, sans-serif;
    font-size: 1.1em;
  }
  </style>
  