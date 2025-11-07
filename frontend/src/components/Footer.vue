<template>
  <!-- Newsletter Section Wrapper -->
  <div class="relative z-20 mx-auto max-w-6xl mt-16 px-4 sm:px-6 lg:px-8">
    <!-- Floating Product Images -->
    <div class="absolute inset-0 z-30 pointer-events-none hidden md:block">
      <img src="/images/footer/footer-strawbery-blur.png" alt="Strawberry" class="absolute top-[-40%] left-[-5%] w-45 h-45" style="animation: bounce-float 6s ease-in-out infinite alternate;" />
      <img src="/images/footer/footer-lemon.png" alt="Lemon" class="absolute bottom-[-50%] right-[0%] w-72 h-72" style="animation: bounce-float 6s ease-in-out infinite alternate;" />
    </div>
    <div class="relative bg-primary py-8 rounded-xl">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div class="text-center">
<h3 class="text-3xl font-dancing-script text-white font-semibold tracking-wide sm:text-3xl md:text-4xl">Newsletter</h3>
          <p class="mt-2 text-sm text-white">Stay updated with exclusive offers and news by subscribing to our newsletter!</p>
        </div>
        <div class="mt-8 flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4">
          <input
            type="email"
            placeholder="Enter your email here"
            class="w-full sm:w-80 px-4 py-2 border border-transparent rounded-lg leading-5 bg-white text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary focus:border-transparent text-sm"
          />
          <button
            @click="handleNewsletterSubmit"
            class="w-1/3 mx-auto sm:w-auto bg-transparent text-white border border-white 
                  px-6 py-2 rounded-lg text-sm font-medium 
                  hover:bg-white hover:text-primary hover:border-transparent 
                  focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary 
                  transition-colors duration-200"
          >
            Submit
          </button>
        </div>
      </div>
    </div>
  </div>

  <footer class="bg-white text-white pt-12">
    <!-- Main Footer Content -->
    <div class="relative bg-primary py-12">
      <img src="/images/footer/footer-right-img.png" alt="Fruit and vegetable market stall" class="absolute top-0 right-0 h-3/4 w-auto object-cover object-center opacity-75 hidden md:block" />

      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 md:pr-1/3 text-center md:text-left">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <!-- Company Info -->
          <div>
            <div class="flex items-center mb-4 justify-center md:justify-start">
              <img src="/images/logos/tunda_logo.png" alt="Tunda Logo" class="h-10 w-auto mr-2 rounded-full bg-white p-1">
              <span class="text-white text-2xl font-bold">Tun<span class="text-orange-400">da</span></span>
            </div>
            <p class="text-gray-300 text-sm mb-2">
              <span class="font-semibold">Address:</span> Queensway House, 3rd Floor, Nairobi
            </p>
            <p class="text-gray-300 text-sm mb-2">
              <span class="font-semibold">Phone No:</span> +254 745 758422
            </p>
            <p class="text-gray-300 text-sm mb-4">
              <span class="font-semibold">Email:</span> hello@gotunda.com
            </p>
            <h4 class="text-lg font-semibold text-white mb-3">Follow Us</h4>
            <div class="flex space-x-3 justify-center md:justify-start">
              <a href="#0" class="text-gray-300 hover:text-white">
                <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path fill-rule="evenodd" d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.776-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33V22C17.343 21.128 22 16.991 22 12z" clip-rule="evenodd" />
                </svg>
              </a>
              <a href="#0" class="text-gray-300 hover:text-white">
                <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12c6.627 0 12-5.373 12-12S18.627 0 12 0zm-2 18H7V9h3v9zm-1.5-9.5c-.828 0-1.5-.672-1.5-1.5S7.672 6.5 8.5 6.5s1.5.672 1.5 1.5-.672 1.5-1.5 1.5zm7 9.5h-3V12c0-1.492-1.008-2-2-2s-2 .508-2 2v6h-3V9h3v1.383c.442-.636 1.225-1.383 2.5-1.383 2.757 0 3.5 1.73 3.5 4.007V18z"/>
                </svg>
              </a>
              <a href="#0" class="text-gray-300 hover:text-white">
                <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path fill-rule="evenodd" d="M12.315 2c2.43 0 2.784.002 3.797.048.843.04 1.105.109 1.734.358.537.254.95.585 1.383 1.017.433.432.764.845 1.018 1.382.249.629.318.891.358 1.734.046 1.013.048 1.371.048 3.797s-.002 2.784-.048 3.797c-.04.843-.109 1.105-.358 1.734-.254.537-.585.95-1.017 1.383-.432.433-.845.764-1.382 1.018-.629.249-.891.318-1.734.358-1.013.045-1.371.048-3.797.048zM12 6.865c-2.89 0-5.235 2.345-5.235 5.235s2.345 5.235 5.235 5.235 5.235-2.345 5.235-5.235-2.345-5.235-5.235-5.235zM12 15.07c-1.795 0-3.25-1.455-3.25-3.25s1.455-3.25 3.25-3.25 3.25 1.455 3.25 3.25-1.455 3.25-3.25 3.25z" clip-rule="evenodd" />
                </svg>
              </a>
              <a href="#0" class="text-gray-300 hover:text-white">
                <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path fill-rule="evenodd" d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-.421.724-.662 1.562-.662 2.432 0 1.72.87 3.213 2.188 4.096-.807-.026-1.566-.247-2.229-.616v.061c0 3.224 2.3 5.894 5.39 6.517-.56.153-1.16.23-1.77.23-.43 0-.84-.04-1.24-.11 1.35.426 2.77.66 4.13.66 3.13 0 6.04-1.62 7.5-4.13.23-.38.36-.81.36-1.26 0-.09 0-.18-.01-.27.94-.68 1.76-1.53 2.41-2.5z" clip-rule="evenodd" />
                </svg>
              </a>
            </div>
          </div>

          <!-- Quick Links -->
          <div>
            <h4 class="text-lg font-semibold text-white mb-4">Quick Links</h4>
            <ul>
              <li class="mb-2"><a href="#0" class="text-gray-300 hover:text-white text-sm">About Us</a></li>
              <li class="mb-2"><a href="#0" class="text-gray-300 hover:text-white text-sm">Blog</a></li>
              <li class="mb-2"><a href="#0" class="text-gray-300 hover:text-white text-sm">Sell With Us</a></li>
            </ul>
          </div>

          <!-- Customer Service -->
          <div>
            <h4 class="text-lg font-semibold text-white mb-4">Customer Service</h4>
            <ul>
              <li class="mb-2"><a href="#0" class="text-gray-300 hover:text-white text-sm">Contact Us</a></li>
              <li class="mb-2"><a href="#0" class="text-gray-300 hover:text-white text-sm">FAQ</a></li>
            </ul>
            <button class="mt-4 bg-yellow-400 text-gray-900 px-6 py-2 rounded-lg text-sm font-medium hover:bg-yellow-500 transition-colors duration-200">
              Shop Now
            </button>
          </div>

          <!-- Legal Information -->
          <div>
            <h4 class="text-lg font-semibold text-white mb-4">Legal Information</h4>
            <ul>
              <li class="mb-2"><a href="#0" class="text-gray-300 hover:text-white text-sm">Privacy Policy</a></li>
              <li class="mb-2"><a href="#0" class="text-gray-300 hover:text-white text-sm">Terms & Conditions</a></li>
              <li class="mb-2"><a href="#0" class="text-gray-300 hover:text-white text-sm">Return And Refund Policy</a></li>
            </ul>
            <div class="flex space-x-2 mt-4 justify-center md:justify-start">
              <!-- Payment Icons - Using placeholder images for now -->
              <img src="/images/footer/paypal.png" alt="PayPal" class="h-6">
              <img src="/images/footer/stripe.png" alt="Stripe" class="h-6">
              <img src="/images/footer/visa.png" alt="Visa" class="h-6">
              <img src="/images/footer/discover.png" alt="Discover" class="h-6">
              <img src="/images/footer/mastercard.png" alt="Mastercard" class="h-6">
            </div>
          </div>
        </div>
      </div>
      <div class="text-center text-gray-400 text-sm mt-8">
        <p>Copyright 2025 Tunda App. All Rights Reserved.</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { ref } from 'vue';

const newsletterEmail = ref('');

const handleNewsletterSubmit = () => {
  console.log('Newsletter subscribed with:', newsletterEmail.value);
  // Add actual subscription logic here
  newsletterEmail.value = ''; // Clear input after submission
};
</script>

<style scoped>
.font-dancing-script {
  font-family: 'Dancing Script', cursive;
}

/* The global bounce-float animation is defined in main.css */
</style>
