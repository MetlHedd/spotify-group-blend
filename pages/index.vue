<template>
  <div class="relative flex items-top justify-center min-h-screen bg-gray-100 sm:items-center sm:pt-0 bg-cover body-img">
    <div class="max-w-4xl mx-auto sm:px-6 lg:px-8">
      <a class="flex justify-center pt-8 sm:pt-0" href="#">
        <img src="/logo.png" />
      </a>
      <div class="mt-8 bg-white overflow-hidden shadow sm:rounded-lg p-6 flex flex-col gap-4 justify-center">
        <div class="flex justify-center">
          <a class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" href="/playlist/new/">
            New Playlist
          </a>
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