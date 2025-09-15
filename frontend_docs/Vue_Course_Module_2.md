# Vue.js Project-Based Learning Course: Tunda Frontend

## Module 2: Vue Components - The Building Blocks of Your UI

### Lesson 2.1: Anatomy of a Single File Component (.vue)

Vue applications are built using components, which are self-contained, reusable blocks of code that encapsulate their own logic, template, and styles. In Vue, these are often referred to as Single File Components (SFCs) and have a `.vue` extension.

An SFC typically consists of three main blocks: `<template>`, `<script>`, and `<style>`.

Let's examine a simple component from your project, `frontend/src/components/HelloWorld.vue`:

```vue
<script setup>
defineProps({
  msg: {
    type: String,
    required: true,
  },
})
</script>

<template>
  <div class="greetings">
    <h1 class="green">{{ msg }}</h1>
    <h3>
      You’ve successfully created a project with
      <a href="https://vite.dev/" target="_blank" rel="noopener">Vite</a> +
      <a href="https://vuejs.org/" target="_blank" rel="noopener">Vue 3</a>.
    </h3>
  </div>
</template>

<style scoped>
h1 {
  font-weight: 500;
  font-size: 2.6rem;
  position: relative;
  top: -10px;
}

h3 {
  font-size: 1.2rem;
}

.greetings h1,
.greetings h3 {
  text-align: center;
}

@media (min-width: 1024px) {
  .greetings h1,
  .greetings h3 {
    text-align: left;
  }
}
</style>

#### 1. The `<template>` Block

*   This section contains the HTML structure of your component.
*   It's where you define what your component will render to the DOM.
*   Vue's templating syntax allows you to bind data, handle events, and conditionally render elements using directives like `{{ }}` (text interpolation), `v-bind:` (or `:`) for attributes, `v-on:` (or `@`) for events, `v-if`, `v-for`, etc.
*   In `HelloWorld.vue`, the template displays a greeting (`msg` prop) and links to Vite and Vue 3 documentation.

#### 2. The `<script setup>` Block

*   This block contains the JavaScript logic for your component.
*   Your project uses `<script setup>`, which is a compile-time sugar for using the Composition API inside Single File Components. It simplifies the component logic by allowing you to write reactive state, computed properties, watchers, and lifecycle hooks directly at the top-level of `<script setup>`, without needing to explicitly define `setup()` or return properties.
*   **`defineProps`**: This is a compiler macro used inside `<script setup>` to declare props. Props are custom attributes you can register on a component. When a value is passed to a prop, it becomes a property on that component instance.
    *   In `HelloWorld.vue`, `defineProps` declares a `msg` prop of type `String` that is `required`. This means any parent component using `HelloWorld` *must* pass a `msg` prop.

#### 3. The `<style>` Block

*   This section contains the CSS rules that style your component's HTML.
*   **`scoped` attribute**: When you add the `scoped` attribute to a `<style>` tag (e.g., `<style scoped>`), the CSS rules inside it will only apply to the elements within the current component's `<template>`. This prevents styles from "leaking" and affecting other components, promoting better encapsulation.
*   In `HelloWorld.vue`, the styles define the appearance of the `h1` and `h3` elements, with a media query for responsive adjustments.

**In summary, a Single File Component (`.vue` file) provides a clean and organized way to develop Vue applications by grouping a component's template, script, and styles into a single file.** This modular approach makes components highly reusable and easier to maintain.

### Lesson 2.2: Props - Passing Data Down

Props are a fundamental mechanism in Vue.js for passing data from a parent component to a child component. This creates a clear and explicit data flow, making your components more predictable and easier to debug.

Let's look at `frontend/src/components/common/ReviewCard.vue` to understand how props are used:

```vue
<script setup>
import { computed } from 'vue'
import { user } from '@/stores/auth'
import { reviewsAPI } from '@/services/api'

const props = defineProps({
  review: {
    type: Object,
    required: true
  },
  showActions: {
    type: Boolean,
    default: false
  },
  showAdminActions: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['edit', 'delete', 'updated'])

// ... (rest of the script logic) ...
</script>

<template>
  <div class="bg-white border border-gray-200 rounded-lg p-4 mb-4">
    <!-- Review Header -->
    <div class="flex items-start justify-between mb-3">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-full flex items-center justify-center" :style="{ backgroundColor: getReviewerColor(review.reviewer) }">
          <span class="text-white font-medium text-sm">
            {{ review.reviewer_username?.charAt(0)?.toUpperCase() || 'A' }}
          </span>
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <!-- Star Rating -->
            <div class="flex items-center">
              <svg v-for="star in 5" :key="star"
                   :class="star <= review.rating ? 'text-yellow-400' : 'text-gray-300'"
                   class="w-4 h-4 fill-current" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
              </svg>
            </div>
            <span class="text-sm text-gray-500">{{ Math.floor(review.rating) }}/5</span>
          </div>
          <h4 class="font-medium text-gray-900 mt-1">— Anonymous</h4>
          <p class="text-xs text-gray-500 mt-1">
            <span v-if="review.is_verified_purchase" class="inline-flex items-center text-green-600 mr-2">
              <div class="relative w-3 h-3 bg-green-500 rounded-full flex items-center justify-center mr-1">
                <svg class="h-2 w-2 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                </svg>
              </div>
              Verified Purchase
            </span>
            {{ formatDate(review.review_date) }}
          </p>
        </div>
      </div>
      
      <!-- Admin Actions -->
      <div v-if="showAdminActions && user?.user_role === 'admin'" class="flex items-center space-x-2">
        <button
          @click="toggleVisibility"
          :class="review.is_visible ? 'text-red-600 hover:text-red-700' : 'text-green-600 hover:text-green-700'"
          class="text-sm font-medium"
        >
          {{ review.is_visible ? 'Hide' : 'Show' }}
        </button>
      </div>
    </div>

    <!-- Review Content -->
    <div v-if="review.comment" class="mb-3">
      <p class="text-gray-700 leading-relaxed">{{ review.comment }}</p>
    </div>

    <!-- Review Photos -->
    <div v-if="review.review_photos && review.review_photos.length > 0" class="mb-3">
      <div class="flex space-x-2 overflow-x-auto">
        <img v-for="(photo, index) in review.review_photos" :key="index"
             :src="photo" :alt="`Review photo ${index + 1}`"
             class="w-20 h-20 object-cover rounded-lg flex-shrink-0">
      </div>
    </div>

    <!-- Action Buttons -->
    <div v-if="showActions" class="flex items-center space-x-2">
      <button v-if="canEdit" @click="$emit('edit', review)"
              class="text-sm text-green-600 hover:text-green-700 font-medium">
        Edit
      </button>
      <button v-if="canDelete" @click="$emit('delete', review)"
              class="text-sm text-red-600 hover:text-red-700 font-medium">
        Delete
      </button>
    </div>
    <span v-if="!review.is_visible && showAdminActions" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 mt-2">
      Hidden
    </span>
  </div>
</template>
```

#### Defining Props with `defineProps`

In the `<script setup>` block of `ReviewCard.vue`, you define the props that this component expects to receive from its parent:

```javascript
const props = defineProps({
  review: {
    type: Object,
    required: true
  },
  showActions: {
    type: Boolean,
    default: false
  },
  showAdminActions: {
    type: Boolean,
    default: false
  }
})
```

*   **`defineProps`**: This is a compiler macro (only available in `<script setup>`) used to declare props. It takes an object where keys are prop names and values are their options.
*   **`review`**:
    *   `type: Object`: Specifies that the `review` prop should be an object.
    *   `required: true`: Means that any component using `ReviewCard` *must* provide a `review` prop; otherwise, Vue will issue a warning. This ensures the component has the necessary data to render.
*   **`showActions`**:
    *   `type: Boolean`: Specifies that `showActions` should be a boolean.
    *   `default: false`: If a parent component doesn't explicitly pass a value for `showActions`, it will default to `false`. This is useful for optional features.
*   **`showAdminActions`**: Similar to `showActions`, this is a boolean prop with a default value.

#### Using Props in the `<template>`

Once props are defined, you can access their values directly in the `<template>` section of your component.

*   **Displaying Review Data**:
    ```html
    <div class="w-10 h-10 rounded-full flex items-center justify-center" :style="{ backgroundColor: getReviewerColor(review.reviewer) }">
      <span class="text-white font-medium text-sm">
        {{ review.reviewer_username?.charAt(0)?.toUpperCase() || 'A' }}
      </span>
    </div>
    <!-- ... -->
    <span class="text-sm text-gray-500">{{ Math.floor(review.rating) }}/5</span>
    <!-- ... -->
    <p class="text-gray-700 leading-relaxed">{{ review.comment }}</p>
    ```
    Here, `review.reviewer_username`, `review.rating`, `review.comment`, `review.review_photos`, `review.is_verified_purchase`, and `review.review_date` are all properties of the `review` object passed via the `review` prop. Vue's `{{ }}` syntax is used to display these values. The `:style` and `:class` bindings dynamically apply styles and classes based on prop values.

*   **Conditional Rendering based on Props**:
    ```html
    <div v-if="showAdminActions && user?.user_role === 'admin'" class="flex items-center space-x-2">
      <!-- ... -->
    </div>
    <!-- ... -->
    <div v-if="showActions" class="flex items-center space-x-2">
      <!-- ... -->
    </div>
    ```
    The `v-if` directive is used to conditionally render entire blocks of HTML based on the boolean values of `showActions` and `showAdminActions` props. This allows the parent component to control which features of the `ReviewCard` are visible.

#### How a Parent Component Passes Props

A parent component would use `ReviewCard` and pass data to its props like this:

```vue
<!-- In a parent component's template -->
<template>
  <ReviewCard 
    :review="someReviewObject" 
    :show-actions="true" 
    :show-admin-actions="isAdminUser" 
    @edit="handleEdit" 
    @delete="handleDelete"
    @updated="handleReviewUpdated"
  />
</template>

<script setup>
import ReviewCard from '@/components/common/ReviewCard.vue'
import { ref } from 'vue'

const someReviewObject = ref({
  review_id: 1,
  reviewer: 101,
  reviewer_username: 'JohnDoe',
  rating: 4.5,
  comment: 'Great product!',
  is_verified_purchase: true,
  review_date: '2023-10-26T10:00:00Z',
  is_visible: true,
  review_photos: []
})

const isAdminUser = ref(true)

const handleEdit = (review) => {
  console.log('Edit review:', review)
  // Logic to open an edit modal
}

const handleDelete = (review) => {
  console.log('Delete review:', review)
  // Logic to confirm and delete review
}

const handleReviewUpdated = (updatedReview) => {
  console.log('Review updated:', updatedReview)
  // Update the review in the parent's data
  someReviewObject.value = updatedReview
}
</script>
```

*   **`:` (v-bind shorthand)**: The colon before `review`, `show-actions`, and `show-admin-actions` is a shorthand for `v-bind:`. It tells Vue to treat the value as a JavaScript expression, not a literal string.
*   **Kebab-case vs. camelCase**: In the template, HTML attributes are typically kebab-case (`show-actions`), while in the `<script setup>` `defineProps` definition, they are camelCase (`showActions`). Vue automatically converts between these two formats.

Understanding props is crucial for building modular and maintainable Vue applications, as it establishes a clear one-way data flow from parent to child components.

### Lesson 2.3: Emits - Communicating Upwards

While props allow data to flow down from parent to child components, **emits** (or custom events) provide a way for child components to communicate back up to their parent components. This is essential for scenarios where a child component needs to notify its parent about an event that has occurred, such as a button click, a form submission, or a modal closing.

Let's examine `frontend/src/components/common/ConfirmModal.vue` to understand how emits are used:

```vue
<template>
  <div v-if="isOpen" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex items-center justify-center">
    <div class="relative mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
      <div class="mt-3 text-center">
        <!-- Icon -->
        <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
          <ExclamationTriangleIcon class="h-6 w-6 text-red-600" />
        </div>
        
        <!-- Title -->
        <h3 class="text-lg leading-6 font-medium text-gray-900 mt-4">
          {{ title }}
        </h3>
        
        <!-- Message -->
        <div class="mt-2 px-7 py-3">
          <p class="text-sm text-gray-500">
            {{ message }}
          </p>
        </div>
        
        <!-- Buttons -->
        <div class="flex justify-center space-x-3 px-4 py-3">
          <button
            @click="$emit('close')"
            class="px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Cancel
          </button>
          <button
            @click="$emit('confirm')"
            class="px-4 py-2 bg-red-600 text-white border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineEmits, defineProps } from 'vue'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true,
  },
  title: {
    type: String,
    default: 'Confirm Action'
  },
  message: {
    type: String,
    default: 'Are you sure you want to perform this action?'
  },
  confirmText: {
    type: String,
    default: 'Confirm'
  }
})

defineEmits(['confirm', 'close'])
</script>
```

#### Declaring Emits with `defineEmits`

In the `<script setup>` block of `ConfirmModal.vue`, you declare the events that this component might emit:

```javascript
defineEmits(['confirm', 'close'])
```

*   **`defineEmits`**: This is a compiler macro (only available in `<script setup>`) used to declare custom events that the component can emit. It takes an array of strings, where each string is the name of an event.
*   By declaring `['confirm', 'close']`, you are telling Vue that `ConfirmModal` can emit two custom events: `confirm` and `close`. This is good practice as it documents the component's interface and allows Vue to provide warnings for undeclared events.

#### Triggering Emits in the `<template>`

You can trigger an event using `$emit('eventName', payload)` directly in the template, typically in response to user interaction.

*   **Closing the Modal**:
    ```html
    <button
      @click="$emit('close')"
      class="px-4 py-2 bg-white text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
    >
      Cancel
    </button>
    ```
    When the "Cancel" button is clicked, `$emit('close')` is called. This sends a `close` event upwards to the parent component.

*   **Confirming an Action**:
    ```html
    <button
      @click="$emit('confirm')"
      class="px-4 py-2 bg-red-600 text-white border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
    >
      {{ confirmText }}
    </button>
    ```
    Similarly, when the "Confirm" button is clicked, `$emit('confirm')` is called, sending a `confirm` event to the parent.

#### Listening to Emitted Events in a Parent Component

A parent component that uses `ConfirmModal` can listen for these custom events using the `v-on:` directive (or its shorthand `@`).

```vue
<!-- In a parent component's template -->
<template>
  <button @click="showModal = true">Open Confirmation</button>

  <ConfirmModal
    :is-open="showModal"
    title="Delete Item"
    message="Are you sure you want to delete this item permanently?"
    confirm-text="Delete"
    @confirm="handleConfirmDelete"
    @close="handleCloseModal"
  />
</template>

<script setup>
import { ref } from 'vue'
import ConfirmModal from '@/components/common/ConfirmModal.vue'

const showModal = ref(false)

const handleConfirmDelete = () => {
  console.log('Action confirmed: Deleting item...')
  // Perform deletion logic here
  showModal.value = false // Close the modal after action
}

const handleCloseModal = () => {
  console.log('Modal closed by user.')
  showModal.value = false // Close the modal
}
</script>
```

*   **`@confirm="handleConfirmDelete"`**: This tells Vue to execute the `handleConfirmDelete` method in the parent component whenever the `ConfirmModal` emits a `confirm` event.
*   **`@close="handleCloseModal"`**: This executes `handleCloseModal` when the `close` event is emitted.

This pattern of props-down, emits-up is a cornerstone of Vue's component communication, ensuring a clear and manageable data flow in your application.

### Lesson 2.4: Component State and Logic

In Vue.js, managing a component's internal data (its "state") and the functions that operate on that data (its "logic" or "methods") is fundamental. With the Composition API (`<script setup>`), Vue 3 provides powerful tools like `ref` and `reactive` for declaring reactive state, and standard JavaScript functions for logic.

Let's examine `frontend/src/components/farmer/CreateProductModal.vue` to understand how state and logic are managed:

```vue
<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center p-4 z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Create New Product</h3>
      </div>

      <form @submit.prevent="handleSubmit" class="px-6 py-4 space-y-4">
        <!-- Product Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Product Name <span class="text-red-500">*</span>
          </label>
          <input
            v-model="formData.product_name"
            type="text"
            required
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Enter product name"
          />
        </div>

        <!-- Category -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Category <span class="text-red-500">*</span>
          </label>
          <select
            v-model="formData.category"
            required
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Select a category</option>
            <option v-for="category in categories" :key="category.category_id" :value="category.category_id">
              {{ category.category_name }}
            </option>
          </select>
        </div>

        <!-- Description -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            v-model="formData.description"
            rows="3"
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholder="Describe the product..."
          ></textarea>
        </div>

        <!-- Unit of Measurement -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Unit of Measurement <span class="text-red-500">*</span>
          </label>
          <select
            v-model="formData.unit_of_measure"
            required
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Select unit</option>
            <option value="kg">Kilogram (kg)</option>
            <option value="piece">Piece</option>
            <option value="bunch">Bunch</option>
            <option value="bag">Bag</option>
            <option value="litre">Litre</option>
          </select>
        </div>

        <!-- Seasonal -->
        <div class="flex items-center">
          <input
            v-model="formData.is_seasonal"
            type="checkbox"
            class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
          />
          <label class="ml-2 block text-sm text-gray-900">
            Seasonal Product
          </label>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="saving"
            class="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
          >
            {{ saving ? 'Creating...' : 'Create Product' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { productsAPI } from '@/services/api'

const emit = defineEmits(['close', 'created'])

// Reactive State
const saving = ref(false)
const categories = ref([])

const formData = reactive({
  product_name: '',
  category: '',
  description: '',
  unit_of_measure: '',
  is_seasonal: false
})

// Methods / Functions
const loadCategories = async () => {
  try {
    const response = await productsAPI.getCategories()
    categories.value = Array.isArray(response) ? response : response.results || []
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const handleSubmit = async () => {
  saving.value = true
  try {
    const response = await productsAPI.createProduct(formData)
    emit('created', response)
    emit('close')
  } catch (error) {
    console.error('Error creating product:', error)
    alert('Failed to create product. Please try again.')
  } finally {
    saving.value = false
  }
}

// Lifecycle Hook
onMounted(() => {
  loadCategories()
})
</script>
```

#### Reactive State with `ref` and `reactive`

In the Composition API, you use `ref` and `reactive` to declare reactive state variables. When these variables change, Vue automatically updates the parts of the DOM that depend on them.

*   **`ref` for Primitive Values and Arrays/Objects**:
    ```javascript
    const saving = ref(false)
    const categories = ref([])
    ```
    `ref` is typically used for primitive values (strings, numbers, booleans) and when you want to replace an entire object or array. It takes an inner value and returns a reactive object with a single property `.value` that points to the inner value. You must access or mutate its value via `.value`.

*   **`reactive` for Objects**:
    ```javascript
    const formData = reactive({
      product_name: '',
      category: '',
      description: '',
      unit_of_measure: '',
      is_seasonal: false
    })
    ```
    `reactive` is used to create reactive objects. It takes an object and returns a reactive proxy of the original object. You can directly access and mutate its properties without using `.value`. It's ideal for grouping multiple related reactive properties, like form data.

#### Methods / Functions

Component logic is encapsulated in functions. In `<script setup>`, you define these functions directly.

*   **`loadCategories`**:
    ```javascript
    const loadCategories = async () => {
      try {
        const response = await productsAPI.getCategories()
        categories.value = Array.isArray(response) ? response : response.results || []
      } catch (error) {
        console.error('Failed to load categories:', error)
      }
    }
    ```
    This asynchronous function fetches product categories from your backend API (`productsAPI.getCategories()`) and updates the `categories` reactive variable. Notice `categories.value` is used because `categories` was declared with `ref`.

*   **`handleSubmit`**:
    ```javascript
    const handleSubmit = async () => {
      saving.value = true
      try {
        const response = await productsAPI.createProduct(formData)
        emit('created', response)
        emit('close')
      } catch (error) {
        console.error('Error creating product:', error)
        alert('Failed to create product. Please try again.')
      } finally {
        saving.value = false
      }
    }
    ```
    This function is called when the form is submitted. It sets a `saving` flag (for UI feedback), calls your API to create a product using the `formData` (which is reactive), emits `created` and `close` events, and handles potential errors.

#### Lifecycle Hooks (`onMounted`)

Lifecycle hooks allow you to run code at specific stages of a component's life (e.g., when it's created, mounted to the DOM, updated, or unmounted).

*   **`onMounted`**:
    ```javascript
    onMounted(() => {
      loadCategories()
    })
    ```
    The `onMounted` hook is called after the component has been mounted to the DOM. In this component, it's used to call `loadCategories()` immediately after the modal appears, ensuring that the category dropdown is populated with data from the API.

#### Using State and Logic in the `<template>`

*   **Two-Way Data Binding (`v-model`)**:
    ```html
    <input v-model="formData.product_name" type="text" required />
    <select v-model="formData.category" required>
      <!-- ... -->
    </select>
    <textarea v-model="formData.description" rows="3"></textarea>
    <input v-model="formData.is_seasonal" type="checkbox" />
    ```
    `v-model` is a powerful directive for creating two-way data bindings on form input elements. It automatically updates the `formData` properties when the input changes, and vice-versa.

*   **Event Handling (`@submit.prevent`, `@click`)**:
    ```html
    <form @submit.prevent="handleSubmit" class="px-6 py-4 space-y-4">
    <!-- ... -->
    <button type="button" @click="$emit('close')">Cancel</button>
    <button type="submit" :disabled="saving">
      {{ saving ? 'Creating...' : 'Create Product' }}
    </button>
    ```
    *   `@submit.prevent="handleSubmit"`: This listens for the form's `submit` event and calls the `handleSubmit` function. The `.prevent` modifier stops the default browser behavior of reloading the page on form submission.
    *   `@click="$emit('close')"`: Triggers the `close` event when the "Cancel" button is clicked.

*   **Conditional Attributes and Text**:
    ```html
    <button type="submit" :disabled="saving">
      {{ saving ? 'Creating...' : 'Create Product' }}
    </button>
    ```
    *   `:disabled="saving"`: The `disabled` attribute of the button is dynamically bound to the `saving` reactive variable. The button will be disabled when `saving` is `true`.
    *   `{{ saving ? 'Creating...' : 'Create Product' }}`: The button's text also changes dynamically based on the `saving` state, providing user feedback.

This `CreateProductModal.vue` component effectively demonstrates how to manage component-specific state and logic using Vue 3's Composition API, making it a robust and interactive part of your application.
