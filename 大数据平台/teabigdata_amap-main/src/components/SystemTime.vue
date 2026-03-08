<template>
  <div class="system-time card">
    <div class="time">{{ timeStr }}</div>
    <div class="date">{{ dateStr }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const timeStr = ref('');
const dateStr = ref('');
let timer = null;

const updateTime = () => {
  const now = new Date();
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');
  timeStr.value = `${hours}:${minutes}:${seconds}`;
  
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  dateStr.value = `${year}-${month}-${day}`;
};

onMounted(() => {
  updateTime();
  timer = setInterval(updateTime, 1000);
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});
</script>

<style scoped>
.system-time {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px 15px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  color: var(--text-color);
  border-radius: 4px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  width: 100%;
  min-width: 220px;
}

.time {
  font-size: 20px;
  font-weight: bold;
  font-family: monospace;
  line-height: 1.2;
  color: var(--primary-color);
}

.date {
  font-size: 12px;
  color: var(--text-color);
  opacity: 0.8;
}
</style>
