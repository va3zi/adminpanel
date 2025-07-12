<template>
  <div class="sa-manage-admins">
    <h3>مدیریت ادمین‌ها</h3>
    <p>در این بخش می‌توانید لیست ادمین‌ها را مشاهده، ادمین جدید اضافه، یا ادمین‌های موجود را ویرایش و حذف کنید.</p>
    <!-- Admin management table and forms will go here -->
    <div class="placeholder-content">
      محتوای مدیریت ادمین‌ها در اینجا قرار خواهد گرفت. (مثلاً جدول ادمین‌ها، دکمه افزودن ادمین جدید)
    </div>
  </div>
</template>

<script>
export default {
  name: 'SAManageAdmins'
}
</script>

<style scoped>
.sa-manage-admins {
  padding: 15px;
  text-align: right;
}
.sa-manage-admins h3 {
  font-size: 1.5em;
  color: #333;
  margin-bottom: 10px;
}
.sa-manage-admins p {
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
