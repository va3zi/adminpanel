<template>
  <div class="sa-manage-plans">
    <h3>مدیریت پلن‌ها</h3>
    <p>در این بخش می‌توانید لیست پلن‌های VPN را مشاهده، پلن جدید اضافه، یا پلن‌های موجود را ویرایش و حذف کنید.</p>
    <!-- Plan management table and forms will go here -->
    <div class="placeholder-content">
      محتوای مدیریت پلن‌ها در اینجا قرار خواهد گرفت. (مثلاً جدول پلن‌ها، دکمه افزودن پلن جدید)
    </div>
  </div>
</template>

<script>
export default {
  name: 'SAManagePlans'
}
</script>

<style scoped>
.sa-manage-plans {
  padding: 15px;
  text-align: right;
}
.sa-manage-plans h3 {
  font-size: 1.5em;
  color: #333;
  margin-bottom: 10px;
}
.sa-manage-plans p {
  font-size: 1em;
  color: #555;
  margin-bottom: 20px;
}
.placeholder-content {
  border: 1px dashed #ccc;
  padding: 20px;
  text-align: center;
  color: #777;
  min-height: 150px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 4px;
}
</style>
