const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  // Output built files to Flask's static/frontend/dist directory
  outputDir: 'dist',
  
  // Configure webpack dev server for development
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000', // Your Flask backend
        changeOrigin: true
      }
    }
  },
  
  // Add proper public path for production
  publicPath: process.env.NODE_ENV === 'production' 
    ? '/static/frontend/dist/' 
    : '/'
})
