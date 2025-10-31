<template>
  <div class="relative bg-green-50 pt-5 pb-20 sm:pt-6 sm:pb-24 lg:pt-8 lg:pb-32">
    <!-- Background Illustration -->
    <div class="absolute inset-0 z-0">
      <img src="/images/explore/explore-background.png" alt="Subtle background illustration" class="w-full h-full object-cover object-center" />
    </div>

    <!-- Floating Product Images -->
    <div class="absolute inset-0 z-10">
      <img src="/images/explore/explore-strawbery-1.png" alt="Strawberry" class="absolute top-[-30%] left-[0%] w-45 h-45" style="animation: float 6s ease-in-out infinite;" />
      <img src="/images/explore/explore-lemon-1.png" alt="Lemon" class="absolute bottom-[10%] left-[15%] w-40 h-40" style="animation: float 7s ease-in-out infinite reverse;" />
      <img src="/images/explore/explore-bucket-1.png" alt="Bucket of Groceries" class="absolute top-[18%] left-[28%] w-[26rem] h-[26rem] -translate-x-1/2 -translate-y-1/2" style="animation: float 8s ease-in-out infinite;" />
      <img src="/images/explore/off-blur-strawbery-2.png" alt="Blurred Strawberry" class="absolute bottom-[10%] right-[15%] w-40 h-40" style="animation: float 5s ease-in-out infinite;" />
      <img src="/images/explore/off-right-lemon-1.png" alt="Blurred Lemon" class="absolute top-[-30%] right-[0%] w-45 h-45" style="animation: float 9s ease-in-out infinite reverse;" />
    </div>

    <div class="relative max-w-7xl mx-auto -ml-4 md:-ml-20 px-4 sm:px-6 lg:px-8 z-20">
      <div class="max-w-2xl ml-auto text-center w-full lg:w-3/4 mt-10"> <!-- Adjusted for subtle right shift, centered text within -->
        <h2 class="text-2xl sm:text-3xl md:text-4xl font-extrabold tracking-tight text-gray-900"> <!-- Increased font size to match HeroSection -->
          <span class="block">30% OFF Deals Inside:</span>
          <span class="block text-green-700">Save Big on Your Favorite Groceries Today!</span>
        </h2>
        <p class="mt-4 text-sm text-gray-600 sm:text-base md:mt-5"> <!-- Kept font size, adjusted for clarity -->
          Discover exclusive discounts and special offers on a wide range of products throughout our
          store. Hurry, while supplies last!
        </p>
        <div class="mt-10">
          <router-link to="/products" class="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-green-600 hover:bg-green-700 md:py-2 md:px-10">
            Explore
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ExploreSection',
}
</script>

<style scoped>
@keyframes float {
  0% { transform: translate(0, 0) rotate(0deg); }
  25% { transform: translate(-5px, -5px) rotate(-2deg); }
  50% { transform: translate(0, -10px) rotate(0deg); }
  75% { transform: translate(5px, -5px) rotate(2deg); }
  100% { transform: translate(0, 0) rotate(0deg); }
}

.absolute img {
  animation-duration: 6s;
  animation-timing-function: ease-in-out;
  animation-iteration-count: infinite;
}
</style>
