<template>
  <div class="not-found-container">
    <h1>404 - صفحه مورد نظر یافت نشد</h1>
    <p>متاسفانه صفحه‌ای که به دنبال آن بودید وجود ندارد.</p>
    <router-link to="/">بازگشت به صفحه اصلی</router-link>
  </div>
</template>

<script>
export default {
  name: 'NotFoundView'
}
</script>

<style scoped>
.not-found-container {
  text-align: center;
  margin-top: 50px;
  padding: 20px;
}
.not-found-container h1 {
  font-size: 2.5em;
  color: #e74c3c;
  margin-bottom: 20px;
}
.not-found-container p {
  font-size: 1.2em;
  margin-bottom: 30px;
}
.not-found-container a {
  color: #3498db;
  text-decoration: none;
  font-weight: bold;
  border: 1px solid #3498db;
  padding: 10px 15px;
  border-radius: 5px;
  transition: background-color 0.3s, color 0.3s;
}
.not-found-container a:hover {
  background-color: #3498db;
  color: white;
}
</style>
