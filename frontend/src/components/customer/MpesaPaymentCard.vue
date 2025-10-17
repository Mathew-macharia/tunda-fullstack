<template>
  <div class="bg-white rounded-lg shadow p-4 sm:p-6 border border-green-200">
    <div class="flex flex-col items-center space-y-4">
      <!-- M-Pesa Logo and "SEND MONEY" -->
      <div class="bg-green-600 w-full py-4 flex flex-col items-center justify-center rounded-t-lg">
        <div class="flex items-center mb-2">
          <span class="text-white text-3xl font-bold">M</span>
          <img src="@/assets/logos/mpesalogo.png" alt="Phone Icon" class="h-10 object-contain mx-1" />
          <span class="text-white text-3xl font-bold">PESA</span>
        </div>
        <p class="text-white text-lg font-bold tracking-wide">SEND MONEY</p>
      </div>

      <!-- Phone Number -->
      <div class="w-full px-4 py-3 border-2 border-green-600 rounded-lg text-center">
        <p class="text-sm font-medium text-gray-700 mb-1">Phone Number</p>
        <p class="text-xl sm:text-2xl font-extrabold text-gray-900">+254 701 669707</p>
      </div>

      <!-- Name -->
      <div class="w-full text-center">
        <p class="text-lg sm:text-xl font-bold text-gray-900">Escrivia Nyongesa</p>
      </div>

      <!-- Instructions and Safaricom -->
      <div class="w-full border-t border-gray-300 pt-4 flex justify-between items-center">
        <p class="text-sm text-gray-600">Go to Mpesa >> Send Money >> Enter Phone Number</p>
        <!-- Safaricom text as no logo was provided -->
        <p class="text-xs font-semibold text-green-700">Safaricom</p>
      </div>

      <!-- Total Amount -->
      <div class="w-full text-center mt-4">
        <p class="text-base text-green-800 font-semibold mb-2">Amount to Pay:</p>
        <p class="font-extrabold text-3xl text-green-700">KSh {{ totalAmount }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MpesaPaymentCard',
  props: {
    totalAmount: {
      type: [String, Number],
      required: true
    }
  }
}
</script>

<style scoped>
/* Add any specific styles here if needed, though Tailwind should handle most */
</style>
