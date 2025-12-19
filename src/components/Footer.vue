<template>
  <footer class="footer">
    <div class="footer-content">
      <p> &copy; 2025 AgriEdu. All rights reserved.</p>
    </div>
  </footer>
</template>

<script>
export default {
  name: "FooterComponent",
};
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap');

.footer {
  background-color:  #0f572b;
  color: #fff;
  padding: 2px;
  margin: 0;
  display: flex; 
  justify-content: center; 
  align-items: center; 
  font-family: 'montserrat';
}

@media (min-width: 600px) {
  .footer-content {
    flex-direction: row;
    justify-content: space-between;
    text-align: left;
  }
}
</style>
