<template>
  <div class="color-lightTheme pt-16">
    <NavBar @toggleMenu="$emit('toggleMenu')" @logout="$emit('logout')" />
    <AccountCard/>
    <Advertisement />
    <VoucherCard/>
    <NewOffers />
    <PackageCard/>
   
    <fooTr/>
    <WelcomeMessage v-if="isNewU" @close="isNewU = false"/>
  </div>
</template>

<script>

import fooTr  from '../components/Footer.vue' 
import WelcomeMessage from '../components/New.vue'
import NavBar from '../components/NavBar.vue'
import AccountCard from '@/components/AccountCard.vue'
import Advertisement from '@/components/Advertisement.vue'
import VoucherCard from '@/components/VoucherCard.vue'
import NewOffers from '@/components/NewOffers.vue'
import PackageCard from '@/components/PackageCard.vue'

export default {
  name: 'ByteDashboard',
  components: {
    NavBar,
    AccountCard,
    Advertisement,
    VoucherCard,
    NewOffers,
    PackageCard,
    fooTr,
    WelcomeMessage
  },
  data() {
    return {
      isNewU: false,
    }
  },
  created() {
    this.isNewU = localStorage.getItem('isNewUser') === 'true';
    localStorage.removeItem('isNewUser');


  },
  methods: {
    
  }
}
</script>

<style>
</style>
