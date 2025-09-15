# Vue.js Project-Based Learning Course: Tunda Frontend

## Module 1: Getting Started with Vue.js & Your Project

### Lesson 1.1: Introduction to Vue.js

Vue.js is a progressive framework for building user interfaces. Unlike other monolithic frameworks, Vue is designed to be incrementally adoptable. This means you can use it to power a small part of an application, or build a full-fledged Single Page Application (SPA) like the "Tunda" frontend.

**Key Features and Advantages:**

*   **Component-Based Architecture:** Vue applications are built using reusable, self-contained components. This promotes modularity and makes your codebase easier to manage.
*   **Reactive Data Binding:** Vue automatically tracks changes to your data and efficiently updates the DOM, simplifying UI development.
*   **Declarative Rendering:** You describe what you want the UI to look like, and Vue takes care of how to achieve it.
*   **Tooling:** Vue offers excellent tooling, including a powerful CLI, DevTools, and integration with modern build tools like Vite (which your project uses).

**Vue 2 vs. Vue 3:**
Your project uses **Vue 3**, as indicated by the `vue` dependency version `^3.5.13` in `frontend/package.json`. Vue 3 introduced several improvements over Vue 2, including:
*   **Composition API:** A new way to organize component logic, offering more flexibility and better reusability, especially for complex components.
*   **Improved Performance:** Faster rendering and smaller bundle sizes.
*   **Teleports, Fragments, and Suspense:** New features for advanced UI patterns.

### Lesson 1.2: Project Setup and Entry Point

This lesson will guide you through understanding how your Vue application is set up and where it all begins.

#### Understanding `package.json`

The `frontend/package.json` file is crucial for any Node.js project, including Vue applications. It defines metadata about the project and manages its dependencies and scripts.

```json
{
  "name": "frontend",
  "version": "0.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@headlessui/vue": "^1.7.23",
    "@heroicons/vue": "^2.2.0",
    "@vueuse/core": "^13.3.0",
    "axios": "^1.9.0",
    "jwt-decode": "^4.0.0",
    "lodash-es": "^4.17.21",
    "pinia": "^3.0.3",
    "vue": "^3.5.13",
    "vue-router": "^4.5.1",
    "vue-toastification": "^2.0.0-rc.5"
  },
  "devDependencies": {
    "@tailwindcss/forms": "^0.5.10",
    "@tailwindcss/typography": "^0.5.16",
    "@vitejs/plugin-vue": "^5.2.3",
    "autoprefixer": "^10.4.21",
    "postcss": "^8.5.4",
    "tailwindcss": "^3.4.17",
    "vite": "^6.2.4",
    "vite-plugin-vue-devtools": "^7.7.2"
  }
}
```

**Key Sections:**

*   **`name`**: The name of your project (`frontend`).
*   **`version`**: The current version of your project.
*   **`private`**: Set to `true` to prevent accidental publication to npm.
*   **`type`**: Set to `module` to enable ES modules syntax.
*   **`scripts`**: Defines command-line scripts that you can run.
    *   `dev`: `vite` - Starts the development server using Vite. You'll use `npm run dev` to run your app locally.
    *   `build`: `vite build` - Compiles your application for production.
    *   `preview`: `vite preview` - Serves the production build locally for testing.
*   **`dependencies`**: Lists the packages required for your application to run in production.
    *   `vue`: The core Vue.js library (version 3).
    *   `pinia`: The official state management library for Vue 3.
    *   `vue-router`: The official routing library for Vue.js.
    *   `axios`: A popular promise-based HTTP client for making API requests.
    *   `jwt-decode`: For decoding JSON Web Tokens (JWTs), likely used for authentication.
    *   `vue-toastification`: For displaying toast notifications.
    *   `@headlessui/vue`, `@heroicons/vue`, `@vueuse/core`, `lodash-es`: Other utility and UI libraries.
*   **`devDependencies`**: Lists packages needed only for development and building, not for the application to run in production.
    *   `vite`: The fast build tool used by your project.
    *   `@vitejs/plugin-vue`: Vite plugin for Vue 3 Single File Components.
    *   `tailwindcss`, `postcss`, `autoprefixer`: For styling with Tailwind CSS.
    *   `vite-plugin-vue-devtools`: A plugin for enhancing the Vue DevTools experience.

#### Running the Development Server

To start your frontend application locally, navigate to the `frontend` directory in your terminal and run:

```bash
npm install # Only run this once to install dependencies
npm run dev
```

This command will start a development server, usually accessible at `http://localhost:5173` (or a similar port).

#### Exploring `frontend/src/main.js`: The Heart of Your Application

The `frontend/src/main.js` file is the entry point of your Vue application. It's the first JavaScript file that gets executed when your application loads.

```javascript
import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { initializeAuth } from '@/stores/auth'

// Initialize auth before mounting app
initializeAuth().then(() => {
  const app = createApp(App) // Creates a new Vue application instance
  app.use(router)            // Integrates Vue Router
  // app.use(pinia)          // Pinia is likely initialized within initializeAuth or implicitly
  app.mount('#app')          // Mounts the application to the HTML element with id 'app'
})
```

**Key Steps in `main.js`:**

1.  **`import './assets/main.css'`**: Imports your global CSS file, applying styles across your application.
2.  **`import { createApp } from 'vue'`**: Imports the `createApp` function from the Vue 3 library, which is used to create a new Vue application instance.
3.  **`import App from './App.vue'`**: Imports your root component, `App.vue`. This component serves as the main container for your entire application.
4.  **`import router from './router'`**: Imports your Vue Router configuration, which defines the navigation paths for your application.
5.  **`import { initializeAuth } from '@/stores/auth'`**: Imports a function from your authentication store. This indicates that authentication logic is initialized early in the application lifecycle.
6.  **`initializeAuth().then(() => { ... })`**: This is an important part. It ensures that your authentication state is initialized *before* the Vue application is mounted. This is a common pattern for applications that require user authentication to function correctly.
7.  **`const app = createApp(App)`**: Creates the actual Vue application instance, using `App.vue` as its root component.
8.  **`app.use(router)`**: Registers Vue Router with your Vue application, making routing functionalities available throughout your components.
9.  **`app.mount('#app')`**: This is the final step where your Vue application is "mounted" to a specific DOM element in your `index.html` file. The `#app` selector means it will look for an element with `id="app"`.

This `main.js` file effectively bootstraps your entire Vue.js application, setting up routing, state management (auth), and mounting the root component.

### Lesson 1.3: The Root Component (`App.vue`)

The `frontend/src/App.vue` file is the root component of your entire Vue.js application. It's the first component loaded and acts as the main layout or shell where all other views and components are rendered.

Your `App.vue` uses the **Composition API** (`<script setup>`), which is the recommended way to write Vue 3 components. This API provides a more flexible and powerful way to organize your component logic compared to the Options API.

#### Anatomy of `App.vue`

```vue
<script setup>
// Imports
import { RouterLink, RouterView } from 'vue-router'
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import logoImage from '@/assets/tunda_logo.jpg'
import { 
  user, 
  isAuthenticated, 
  isCustomer, 
  isFarmer, 
  isRider, 
  isAdmin,
  getUserName,
  logout,
  guestCartItems
} from '@/stores/auth'
import { cartAPI, communicationAPI } from '@/services/api'

// Reactive State (using ref)
const router = useRouter()
const showUserDropdown = ref(false)
const showMobileMenu = ref(false)
const searchQuery = ref('')
const authenticatedCartCount = ref(0)
const activeTicketsCount = ref(0)

// Computed Properties
const cartCount = computed(() => {
  if (isAuthenticated.value && isCustomer.value) {
    return authenticatedCartCount.value
  } else {
    return guestCartItems.value.length
  }
})

// Functions/Methods
const loadCartCount = async () => { /* ... */ }
const loadActiveTicketsCount = async () => { /* ... */ }
const navigateToSupport = () => { /* ... */ }
const handleCartUpdate = () => { /* ... */ }
const handleLogout = async () => { /* ... */ }
const handleSearch = () => { /* ... */ }
const closeDropdowns = (event) => { /* ... */ }

// Watchers
watch(isAuthenticated, (newValue) => { /* ... */ })
watch(isAdmin, (newValue) => { /* ... */ })

// Lifecycle Hooks
onMounted(() => { /* ... */ })
onUnmounted(() => { /* ... */ })
</script>

<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Navigation Bar -->
    <nav class="bg-white shadow-sm sticky top-0 z-50">
      <!-- ... (Navigation content) ... -->
    </nav>
    
    <!-- Overlay -->
    <div v-show="showMobileMenu" 
         @click="showMobileMenu = false"
         class="fixed top-16 inset-x-0 bottom-0 bg-black bg-opacity-25 z-40 md:hidden"></div>
    
    <!-- Main Content Area for Router Views -->
    <RouterView />
  </div>
</template>
```

**Key Elements in `App.vue`:**

1.  **`<script setup>`**:
    *   This is a syntactic sugar for using the Composition API in Single File Components. It allows you to declare reactive state, computed properties, watchers, and lifecycle hooks directly at the top-level of `<script setup>` without needing to explicitly return them.
    *   **Imports**: You'll notice imports for:
        *   `RouterLink`, `RouterView`: Components provided by Vue Router for navigation and rendering route-matched components.
        *   `ref`, `computed`, `onMounted`, `onUnmounted`, `watch`: Core Vue 3 Composition API functions for reactivity and lifecycle management.
        *   `useRouter`: A Composition API function to access the router instance.
        *   `logoImage`: An asset imported directly.
        *   `auth` store functions (`isAuthenticated`, `user`, `logout`, etc.): These are imported from `frontend/src/stores/auth.js`, demonstrating how your root component interacts with global state management.
        *   `cartAPI`, `communicationAPI`: Imported from `frontend/src/services/api.js`, showing integration with your backend API.
    *   **Reactive State (`ref`)**: Variables like `showUserDropdown`, `showMobileMenu`, `searchQuery` are declared using `ref()`. `ref` is a function that takes an inner value and returns a reactive and mutable ref object. You access its value using `.value`.
    *   **Computed Properties (`computed`)**: `cartCount` is a `computed` property. It automatically re-evaluates its value when its dependencies (like `isAuthenticated` or `guestCartItems`) change. This is efficient for displaying derived data.
    *   **Functions/Methods**: `loadCartCount`, `handleLogout`, `handleSearch`, etc., are functions that encapsulate the component's logic.
    *   **Watchers (`watch`)**: `watch(isAuthenticated, ...)` and `watch(isAdmin, ...)` are used to perform side effects (like loading cart data or active tickets) when specific reactive data sources change.
    *   **Lifecycle Hooks (`onMounted`, `onUnmounted`)**:
        *   `onMounted()`: This hook runs after the component has been mounted to the DOM. Here, it's used to add event listeners for closing dropdowns and updating the cart, and to load initial data.
        *   `onUnmounted()`: This hook runs when the component is unmounted (removed from the DOM). It's crucial for cleaning up event listeners to prevent memory leaks.

2.  **`<template>`**:
    *   This section defines the HTML structure of your root component.
    *   **`id="app"`**: This `div` matches the `#app` selector used in `main.js` for mounting the Vue application.
    *   **Navigation Bar (`<nav>`)**: Contains the main navigation elements, including the logo, product links, search bars (desktop and mobile), cart icon, support button, and user authentication/profile menu.
        *   **`RouterLink`**: Used for declarative navigation within your Vue application. When clicked, it changes the URL without a full page reload.
        *   **`v-if` / `v-show`**: Directives used for conditional rendering. `v-if` completely removes/adds elements from the DOM, while `v-show` toggles their CSS `display` property.
        *   **`v-model`**: Used for two-way data binding on the search input (`searchQuery`).
        *   **`@click` / `@keyup.enter`**: Event listeners for user interactions.
        *   **Tailwind CSS Classes**: The extensive use of classes like `bg-white`, `shadow-sm`, `flex`, `hidden md:block` indicates that your project uses Tailwind CSS for styling, which is a utility-first CSS framework.
    *   **`<RouterView />`**: This is a crucial component from Vue Router. It acts as a placeholder where the component corresponding to the current route will be rendered. When you navigate to `/products`, the `ProductsPage.vue` component (or whatever is mapped to `/products` in `router/index.js`) will be rendered inside `RouterView`.

In summary, `App.vue` is a comprehensive root component that sets up the overall layout, handles global navigation, manages user authentication and cart state, and provides a responsive user experience. It's an excellent example of a complex Vue 3 component utilizing the Composition API and integrating with various parts of your application's architecture.
