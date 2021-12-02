<template>
  <div class="relative flex items-top justify-center min-h-screen bg-gray-100 sm:items-center sm:pt-0 bg-cover body-img">
    <div class="max-w-4xl mx-auto sm:px-6 lg:px-8">
      <a class="flex justify-center pt-8 sm:pt-0" href="https://nuxtjs.org" target="_blank">
        <img src="/logo.png" />
      </a>
      <div class="mt-8 bg-white overflow-hidden shadow sm:rounded-lg p-6">
        <div class="flex justify-center flex-col gap-4">
          <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" type="button" @click="copyURL">
            Copy link and share to your friends
          </button>
          <a class="bg-indigo-500 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline text-center" type="button" :href="`/playlist/add_on/${$route.params.slug}`">
            Add myself to the playlist
          </a>
        </div>
      </div>
      <div class="mt-8 bg-white shadow sm:rounded-lg p-6">
        <div class="block text-gray-700 text-sm font-bold mb-2">
          Added users:
        </div>
        <div v-if="users.length == 0" class="text-gray-700 text-sm font-bold mb-2 invisible">
          Nothing to show here!
        </div>
        <div class="grid grid-cols-3 gap-2 justify-items-center">
          <div v-for="user in users" :key="user" class="bg-black hover:bg-red-500 text-white font-bold p-2 rounded cursor-pointer">{{user.name}}</div>
        </div>
      </div>
      <div class="mt-8 bg-white shadow sm:rounded-lg p-6 flex justify-center">
        <button class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" type="button" @click="generateBlend">
          Generate group blend
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      users: []
    }
  },
  created() {
    axios(`/playlist/has/${this.$route.params.slug}`)
      .then(res => {
        if (res.data.status === 'ok') {
          this.users = res.data.users
        } else {
          this.$router.push('/#playlist_not_found')
        }
      })
  },
  methods: {
    generateBlend() {
      axios.get(`/playlist/generate/${this.$route.params.slug}`)
        .then(res => {
          if (res.data.status === 'ok') {
            this.$router.push(`/playlist/${this.$route.params.slug}`)
          } else {
            this.$router.push('/#generator_error')
          }
        })
    },
    copyURL() {
      navigator.clipboard.writeText(`${window.location.origin}/playlist/${this.$route.params.slug}`)
    }
  }
}
</script>

<style scoped>
.body-img {
  background-image: linear-gradient(rgba(255, 255, 255, 0.44), rgba(0, 0, 0, 0.88)), url('/wallpaper.jpg');
}
</style>
