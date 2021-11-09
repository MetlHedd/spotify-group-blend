<template>
  <div class="relative flex items-top justify-center min-h-screen bg-gray-100 sm:items-center sm:pt-0 bg-cover body-img">
    <div class="max-w-4xl mx-auto sm:px-6 lg:px-8">
      <a class="flex justify-center pt-8 sm:pt-0" href="https://nuxtjs.org" target="_blank">
        <img src="/logo.png" />
      </a>
      <div class="mt-8 bg-white overflow-hidden shadow sm:rounded-lg p-6">
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2" for="username">
            Username to add to the playlist
          </label>
          <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="username" type="text" placeholder="Username">
        </div>
        <div>
          <button class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" type="button">
            Add
          </button>
        </div>
      </div>
      <div class="mt-8 bg-white shadow sm:rounded-lg p-6">
        <div class="block text-gray-700 text-sm font-bold mb-2">
          Added users:
        </div>
        <div class="block text-gray-700 text-sm font-bold mb-2 invisible">
          Nothing to show here!
        </div>
        <div class="grid grid-cols-3 gap-2 justify-items-center">
          <div class="bg-black hover:bg-red-500 text-white font-bold p-2 rounded cursor-pointer">Username</div>
          <div class="bg-black hover:bg-red-500 text-white font-bold p-2 rounded cursor-pointer">Username</div>
          <div class="bg-black hover:bg-red-500 text-white font-bold p-2 rounded cursor-pointer">Username</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {}
</script>

<style scoped>
.body-img {
  background-image: linear-gradient(rgba(255, 255, 255, 0.44), rgba(0, 0, 0, 0.88)), url('/wallpaper.jpg');
}
</style>