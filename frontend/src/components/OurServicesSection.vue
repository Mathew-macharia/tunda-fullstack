<template>
  <div class="relative pt-5 pb-20 sm:pt-6 sm:pb-24 lg:pt-8 lg:pb-32">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
      <p class="text-2xl text-gray-900 font-semibold tracking-wide uppercase font-dancing-script">Our</p>
      <h2 class="mt-2 text-4xl font-extrabold text-green-600 tracking-tight sm:text-4xl">
        Services
      </h2>
    </div>

    <div class="relative mt-4 py-12 sm:py-20">
      <!-- Background Illustration -->
      <div class="absolute inset-0 z-0">
        <img src="/images/services/service-background.PNG" alt="Subtle background illustration" class="w-full h-full object-cover lg:object-contain" />
      </div>

      <!-- Floating Product Images and Man Image -->
      <div class="absolute inset-0 z-30 hidden lg:block">
        <img src="/images/services/service-strawbery-blur-1.png" alt="Strawberry" class="absolute top-[-25%] left-[30%] max-w-64 max-h-64 object-contain" style="animation: float 6s ease-in-out infinite; width: auto; height: auto;" />
        <img src="/images/services/service-blur-mango-1.png" alt="Mango" class="absolute bottom-[5%] right-[0%] max-w-64 max-h-64 object-contain" style="animation: float 7s ease-in-out infinite reverse; width: auto; height: auto;" />
        <img src="/images/services/service-cabbage-1.png" alt="Cabbage" class="absolute bottom-[-15%] left-[0%] max-w-64 max-h-64 object-contain" style="animation: float 8s ease-in-out infinite; width: auto; height: auto;" />
        <img src="/images/services/service-bottle-right-2.png" alt="Bottle" class="absolute top-[-15%] right-[0%] max-w-64 max-h-64 object-contain" style="animation: float 5s ease-in-out infinite; width: auto; height: auto;" />
        <!-- Man Image -->
        <img src="/images/services/service-man.png" alt="Delivery Man" class="absolute top-[5%] left-[-12%] w-120 h-120" />
      </div>

      <div class="relative max-w-5xl mx-auto px-4 sm:px-8 lg:px-12 z-20 flex flex-col lg:flex-row items-center">
        <!-- Service Details -->
        <div class="lg:w-2/3 max-w-xl lg:ml-auto lg:mr-24 lg:pr-8 text-center lg:text-left">
          <div class="space-y-6">

            <!-- One Day Service -->
            <!-- Mobile Layout -->
            <div class="flex flex-col items-center lg:hidden">
              <div class="flex items-center space-x-2">
                <img src="/images/services/service-icon1-1.png" alt="One Day Icon" class="flex-shrink-0 w-10 h-10" />
                <h3 class="text-lg text-gray-900">One Day</h3>
              </div>
              <p class="mt-1 text-sm text-gray-600">Experience lightning-fast delivery with our one-day shipping service, ensuring your groceries arrive when you need them most.</p>
            </div>
            <!-- Laptop Layout -->
            <div class="hidden lg:flex items-start lg:items-center lg:space-x-4">
              <img src="/images/services/service-icon1-1.png" alt="One Day Icon" class="flex-shrink-0 w-10 h-10" />
              <div>
                <h3 class="text-lg text-gray-900">One Day</h3>
                <p class="mt-1 text-sm text-gray-600">Experience lightning-fast delivery with our one-day shipping service, ensuring your groceries arrive when you need them most.</p>
              </div>
            </div>

            <!-- 24x7 Service -->
            <!-- Mobile Layout -->
            <div class="flex flex-col items-center lg:hidden">
              <div class="flex items-center space-x-2">
                <img src="/images/services/service-icon2-1.png" alt="24x7 Icon" class="flex-shrink-0 w-10 h-10" />
                <h3 class="text-lg text-gray-900">24x7</h3>
              </div>
              <p class="mt-1 text-sm text-gray-600">Our customer service team is available round-the-clock, 24/7, ready to assist you with any inquiries.</p>
            </div>
            <!-- Laptop Layout -->
            <div class="hidden lg:flex items-start lg:items-center space-x-4 lg:ml-16">
              <img src="/images/services/service-icon2-1.png" alt="24x7 Icon" class="flex-shrink-0 w-10 h-10" />
              <div>
                <h3 class="text-lg text-gray-900">24x7</h3>
                <p class="mt-1 text-sm text-gray-600">Our customer service team is available round-the-clock, 24/7, ready to assist you with any inquiries.</p>
              </div>
            </div>

            <!-- Verified Farmers Service -->
            <!-- Mobile Layout -->
            <div class="flex flex-col items-center lg:hidden">
              <div class="flex items-center space-x-2">
                <img src="/images/services/service-icon3-1.png" alt="Verified Farmers Icon" class="flex-shrink-0 w-10 h-10" />
                <h3 class="text-lg text-gray-900">Verified Farmers</h3>
              </div>
              <p class="mt-1 text-sm text-gray-600">Shop from verified Farmers with guaranteed quality and authenticity standards.</p>
            </div>
            <!-- Laptop Layout -->
            <div class="hidden lg:flex items-start lg:items-center space-x-4 lg:ml-32">
              <img src="/images/services/service-icon3-1.png" alt="Verified Farmers Icon" class="flex-shrink-0 w-10 h-10" />
              <div>
                <h3 class="text-lg text-gray-900">Verified Farmers</h3>
                <p class="mt-1 text-sm text-gray-600">Shop from verified Farmers with guaranteed quality and authenticity standards.</p>
              </div>
            </div>

            <!-- 100% Service -->
            <!-- Mobile Layout -->
            <div class="flex flex-col items-center lg:hidden">
              <div class="flex items-center space-x-2">
                <img src="/images/services/service-icon4-1.png" alt="100% Icon" class="flex-shrink-0 w-10 h-10" />
                <h3 class="text-xl text-gray-900">100%</h3>
              </div>
              <p class="mt-1 text-sm text-gray-600">Shop confidently with our 100% assured products, backed by our commitment to quality and customer satisfaction, ensuring every purchase exceeds your expectations.</p>
            </div>
            <!-- Laptop Layout -->
            <div class="hidden lg:flex items-start lg:items-center space-x-4 lg:ml-20">
              <img src="/images/services/service-icon4-1.png" alt="100% Icon" class="flex-shrink-0 w-10 h-10" />
              <div>
                <h3 class="text-xl text-gray-900">100%</h3>
                <p class="mt-1 text-sm text-gray-600">Shop confidently with our 100% assured products, backed by our commitment to quality and customer satisfaction, ensuring every purchase exceeds your expectations.</p>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'OurServicesSection',
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

.font-dancing-script {
  font-family: 'Dancing Script', cursive;
}
</style>
