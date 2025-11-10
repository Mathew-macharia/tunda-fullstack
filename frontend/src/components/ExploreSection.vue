<template>
  <div class="relative bg-primary pt-5 pb-20 sm:pt-6 sm:pb-24 lg:pt-8 lg:pb-32">
    <!-- Background Illustration -->
    <div class="absolute inset-0 z-0">
      <img src="/images/explore/explore-background.png" alt="Subtle background illustration" class="w-full h-full object-cover object-center" />
    </div>

    <!-- Floating Product Images -->
    <div class="absolute inset-0 z-10 hidden sm:block">
      <img src="/images/explore/explore-strawbery-1.png" alt="Strawberry" class="absolute top-[-30%] left-[0%] w-45 h-45 animated-float-image" />
      <img src="/images/explore/explore-lemon-1.png" alt="Lemon" class="absolute bottom-[10%] left-[15%] w-40 h-40 animated-float-image" />
      <img src="/images/explore/explore-bucket-1.png" alt="Bucket of Groceries" class="absolute top-[18%] left-[28%] w-[26rem] h-[26rem] -translate-x-1/2 -translate-y-1/2" />
      <img src="/images/explore/off-blur-strawbery-2.png" alt="Blurred Strawberry" class="absolute bottom-[10%] right-[15%] w-40 h-40 animated-float-image" />
      <img src="/images/explore/off-right-lemon-1.png" alt="Blurred Lemon" class="absolute top-[-30%] right-[0%] w-45 h-45 animated-float-image" />
    </div>

    <div class="relative max-w-7xl mx-auto -ml-4 md:-ml-20 px-4 sm:px-6 lg:px-8 z-20">
      <div class="max-w-2xl ml-auto text-center w-full lg:w-3/4 mt-10"> <!-- Adjusted for subtle right shift, centered text within -->
        <h2 class="text-2xl sm:text-3xl md:text-4xl font-extrabold tracking-tight text-gray-900"> <!-- Increased font size to match HeroSection -->
          <span class="block">30% OFF Deals Inside:</span>
          <span class="block text-primary">Save Big on Your Favorite Groceries Today!</span>
        </h2>
        <p class="mt-4 text-sm text-gray-600 sm:text-base md:mt-5"> <!-- Kept font size, adjusted for clarity -->
          Discover exclusive discounts and special offers on a wide range of products throughout our
          store. Hurry, while supplies last!
        </p>
        <div class="mt-10 flex justify-center">
          <router-link to="/products" class="inline-flex items-center justify-center px-2 md:px-7 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-darkGreen md:py-2.5 md:text-base">
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
/* The global bounce-float animation is defined in main.css */
</style>
