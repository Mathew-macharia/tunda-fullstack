<template>
  <div class="relative bg-primary py-20 sm:py-32 lg:py-40 overflow-visible">
    <!-- Background Illustrations -->
    <div class="absolute inset-0 z-0">
      <img src="/images/backgrounds/background_image.png" alt="Background illustrations" class="w-full h-full object-cover object-center" />
    </div>

    <!-- Floating Product Images -->
    <div class="absolute z-10 w-full h-full pointer-events-none">
      <!-- Hidden on mobile, visible on md and up -->
      <img src="/images/hero/red_tomato.png" alt="Red Tomato" class="hidden md:block absolute bottom-[20%] left-[25%] w-24 h-24 lg:w-32 lg:h-32 xl:w-36 xl:h-36 -translate-x-1/2 -translate-y-1/2 rotate-0" style="animation: float 6s ease-in-out infinite;" />
      <img src="/images/hero/yellow_bell_pepper.png" alt="Yellow Bell Pepper" class="hidden md:block absolute bottom-[20%] right-[25%] w-24 h-24 lg:w-32 lg:h-32 xl:w-36 xl:h-36 translate-x-1/2 -translate-y-1/2 -rotate-6" style="animation: float 7s ease-in-out infinite reverse;" />
      <img src="/images/hero/broccoli.png" alt="Broccoli" class="hidden md:block absolute top-[5%] left-[4%] w-24 h-24 lg:w-32 lg:h-32 xl:w-36 xl:h-36 -translate-x-1/2 translate-y-1/2 rotate-3" style="animation: float 5s ease-in-out infinite;" />
      
      <!-- Basket - visible on all screens but scaled down on mobile, brought forward with z-50 -->
      <!-- Mobile: bottom-[5%] (very low), Tablet/Desktop: bottom-[35%] (original) -->
      <img src="/images/hero/basket_of_grocerries.png" alt="Basket of Groceries" class="absolute bottom-[25%] md:bottom-[35%] left-1/2 w-64 h-64 sm:w-80 sm:h-80 lg:w-96 lg:h-96 -translate-x-1/2 translate-y-1/2 z-50" style="animation: float 8s ease-in-out infinite;" />
      
      <!-- Hidden on mobile, visible on md and up -->
      <img src="/images/hero/Swiss_chard.png" alt="Swiss Chard" class="hidden md:block absolute top-[5%] right-[0%] w-24 h-24 lg:w-32 lg:h-32 xl:w-36 xl:h-36" style="animation: float 6s ease-in-out infinite reverse;" />
      <img src="/images/hero/top-bottol-blur-1.png" alt="Top Bottle" class="hidden md:block absolute bottom-[20%] right-[0%] w-20 h-20 lg:w-24 lg:h-24 xl:w-28 xl:h-28" style="animation: float 5s ease-in-out infinite;" />
      <img src="/images/hero/top-mirchi-blur-1.png" alt="Top Mirchi" class="hidden md:block absolute top-[15%] right-[24%] w-16 h-16 lg:w-20 lg:h-20" style="animation: float 7s ease-in-out infinite reverse;" />
      <img src="/images/hero/top-tomato-blur-1.png" alt="Top Tomato Blue" class="hidden md:block absolute top-[-30%] left-[10%] w-16 h-16 lg:w-20 lg:h-20 rotate-6" style="animation: float 6s ease-in-out infinite;" />
    </div>

    <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center" style="transform: translateY(-30%);">
        <h1 class="text-2xl font-extrabold tracking-tight text-grey-900 sm:text-3xl md:text-4xl">
          <span class="block xl:inline">Fresh From Farmers</span>
          <span class="block text-primary xl:inline"> Right to Your Doorstep.</span>
        </h1>
        <p class="mt-4 max-w-2xl mx-auto text-sm text-gray-500 sm:text-base md:mt-5 md:max-w-3xl">
          Experience groceries that haven't forgotten their roots. Picked by local farmers at dawn, we deliver them to your doorstep before the day fades. No warehouses. No markups. Just food in its purest form!
        </p>
        <div class="mt-8 sm:mt-10 max-w-sm mx-auto sm:max-w-none sm:flex sm:justify-center">
          <div class="space-y-4 sm:space-y-0 sm:mx-auto sm:inline-grid sm:grid-cols-1 sm:gap-5">
            <router-link to="/products" class="inline-flex md:flex items-center justify-center px-2 md:px-7 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-darkGreen md:py-2.5 md:text-base">
              Start Shopping
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Badge - Repositioned for mobile responsiveness -->
    <div class="absolute bottom-[15%] sm:bottom-[20%] right-[5%] sm:right-[15%] lg:right-[28%] z-20">
      <div class="bg-white rounded-lg sm:rounded-xl shadow-lg px-3 py-1.5 sm:px-4 sm:py-2 flex flex-col items-start space-y-0.5 sm:space-y-1">
        <div class="flex items-center space-x-1">
          <svg class="h-4 w-4 sm:h-5 sm:w-5 lg:h-6 lg:w-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <span class="text-xs sm:text-sm lg:text-base font-bold text-gray-700">100% Fresh</span>
        </div>
        <div class="flex items-center space-x-1">
          <svg class="h-4 w-4 sm:h-5 sm:w-5 lg:h-6 lg:w-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <span class="text-xs sm:text-sm lg:text-base font-light text-gray-700">Super Fast Delivery</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HeroSection',
}
</script>

<style scoped>
@keyframes float {
  0% { transform: translate(0, 0); }
  50% { transform: translate(0, -10px); }
  100% { transform: translate(0, 0); }
}

.absolute img {
  animation-duration: 6s;
  animation-timing-function: ease-in-out;
  animation-iteration-count: infinite;
}
</style>
