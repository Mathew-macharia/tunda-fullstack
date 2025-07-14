<template>
  <TransitionRoot as="template" :show="show">
    <Dialog as="div" class="relative z-10" @close="emit('close')">
      <TransitionChild
        as="template"
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
      </TransitionChild>

      <div class="fixed inset-0 z-10 overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild
            as="template"
            enter="ease-out duration-300"
            enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to="opacity-100 translate-y-0 sm:scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 translate-y-0 sm:scale-100"
            leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          >
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <div>
                <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-green-100">
                  <CurrencyDollarIcon class="h-6 w-6 text-green-600" aria-hidden="true" />
                </div>
                <div class="mt-3 text-center sm:mt-5">
                  <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">Request Payout</DialogTitle>
                  <div class="mt-2">
                    <p class="text-sm text-gray-500">
                      Enter the amount you wish to withdraw from your available balance.
                    </p>
                    <p class="text-sm font-medium text-gray-700 mt-1">
                      Available Balance: KES {{ formatCurrency(availableBalance) }}
                    </p>
                  </div>
                  <div class="mt-4">
                    <label for="payout-amount" class="sr-only">Payout Amount</label>
                    <div class="relative rounded-md shadow-sm">
                      <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                        <span class="text-gray-500 sm:text-sm">KES</span>
                      </div>
                      <input
                        type="number"
                        name="payout-amount"
                        id="payout-amount"
                        v-model="payoutAmount"
                        @input="validateAmount"
                        class="block w-full rounded-md border-0 py-1.5 pl-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-green-600 sm:text-sm sm:leading-6"
                        placeholder="0.00"
                        :aria-invalid="!!payoutError"
                        aria-describedby="payout-amount-error"
                      />
                    </div>
                    <p v-if="payoutError" class="mt-2 text-sm text-red-600" id="payout-amount-error">
                      {{ payoutError }}
                    </p>
                  </div>
                </div>
              </div>
              <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                <button
                  type="button"
                  class="inline-flex w-full justify-center rounded-md bg-green-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-green-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-green-600 sm:col-start-2"
                  @click="requestPayout"
                  :disabled="!isValidPayoutAmount || requestingPayout"
                >
                  <span v-if="requestingPayout">Requesting...</span>
                  <span v-else>Request Payout</span>
                </button>
                <button
                  type="button"
                  class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0"
                  @click="emit('close')"
                  ref="cancelButtonRef"
                >
                  Cancel
                </button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { CurrencyDollarIcon } from '@heroicons/vue/24/outline'
import { financeAPI } from '@/services/api'
import { user } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  availableBalance: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['close', 'payoutRequested'])

const payoutAmount = ref('')
const payoutError = ref('')
const requestingPayout = ref(false)
const toast = useToast()

const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-KE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount || 0)
}

const isValidPayoutAmount = computed(() => {
  const amount = Number(payoutAmount.value)
  return amount > 0 && amount <= props.availableBalance
})

const validateAmount = () => {
  const amount = Number(payoutAmount.value)
  if (isNaN(amount) || amount <= 0) {
    payoutError.value = 'Please enter a valid positive amount.'
  } else if (amount > props.availableBalance) {
    payoutError.value = `Amount cannot exceed your available balance (KES ${formatCurrency(props.availableBalance)}).`
  } else {
    payoutError.value = ''
  }
}

const requestPayout = async () => {
  validateAmount()
  if (payoutError.value) {
    return
  }

  requestingPayout.value = true
  try {
    await financeAPI.createPayout({
      amount: Number(payoutAmount.value),
      user: user.value.id
    })
    toast.success('Payout request submitted successfully!')
    emit('payoutRequested')
    emit('close')
    payoutAmount.value = ''
  } catch (error) {
    toast.error('Failed to submit payout request.')
    console.error('Error requesting payout:', error)
    payoutError.value = error.response?.data?.detail || 'An unexpected error occurred.'
  } finally {
    requestingPayout.value = false
  }
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    payoutAmount.value = ''
    payoutError.value = ''
  }
})
</script>
