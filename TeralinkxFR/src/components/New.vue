<template>
    <div class="overlay" @click.self="close">
      <div class="welcome-message">
        <button class="close-button" @click="close">
          <i class="fas fa-times"></i>
        </button>
        <h1>Welcome to TERALINKX WAVES!</h1>
        <p class="italic-text">The gateway to your online services</p>
        <p>We're glad to have you here. Enjoy your first 30 MINUTES UNLIMITED package .</p>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'WelcomeMessage',
    props: {
      userName: {
        type: String,
        required: true
      }
    },
    methods: {
      close() {
        this.$emit('close');
      }
    }
  }
  </script>
  
  <style scoped>
  .overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.6);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }
  
  .welcome-message {
    background-color: rgba(255, 255, 255, 0.95);
    padding: 30px;
    border-radius: 15px;
    text-align: center;
    position: relative;
    color: #023016;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    max-width: 90%;
    width: 400px;
  }
  
  .close-button {
    position: absolute;
    top: 10px;
    right: 10px;
    background: none;
    border: none;
    font-size: 1.8em;
    cursor: pointer;
    transition: color 0.3s ease;
  }
  
  .close-button i .fa-times {
    color: #ce4545;
  }
  
  .close-button .fa-times:hover {
    color: #c00;
  }
  
  h1 {
    font-weight: 700;
    margin-bottom: 10px;
  }
  
  .italic-text {
    font-style: italic;
    margin: 10px 0;
  }
  
  p {
    margin: 0;
    font-size: 1.1em;
  }
  
  @media (max-width: 768px) {
    .welcome-message {
      padding: 20px;
      max-width: 80%;
      width: auto;
    }
  
    .close-button {
      font-size: 1.5em;
    }
  
    h1 {
      font-size: 1.5em;
    }
  
    p {
      font-size: 1em;
    }
  }
  
  @media (max-width: 480px) {
    .welcome-message {
      padding: 15px;
      max-width: 90%;
    }
  
    .close-button {
      font-size: 1.2em;
    }
  
    h1 {
      font-size: 1.2em;
    }
  
    p {
      font-size: 0.9em;
    }
  }
  </style>
  
