<template>
  <footer class="footer">
    <div class="footer-main">
      <div class="footer-brand-col">
        <div class="footer-brand">💎 珑饰</div>
        <div class="footer-tagline">智能珠宝电商平台，AI 精准推荐 + AR 虚拟试戴，让每一件饰品都恰到好处。</div>
        <div class="footer-socials">
          <span class="footer-social-btn">微</span>
          <span class="footer-social-btn">博</span>
          <span class="footer-social-btn">抖</span>
        </div>
      </div>
      <div class="footer-col">
        <h4>商品分类</h4>
        <router-link to="/goods?cat=earring">耳饰</router-link>
        <router-link to="/goods?cat=necklace">项链</router-link>
        <router-link to="/goods?cat=bracelet">手链</router-link>
        <router-link to="/goods?cat=ring">戒指</router-link>
      </div>
      <div class="footer-col">
        <h4>智能服务</h4>
        <router-link to="/ai-guide">AI 智能导购</router-link>
        <router-link to="/face-detect">脸型分析</router-link>
        <router-link to="/goods">AR 虚拟试戴</router-link>
      </div>
      <div class="footer-col">
        <h4>帮助中心</h4>
        <a href="#">常见问题</a>
        <a href="#">退换货政策</a>
        <a href="#">联系客服</a>
        <a href="#">用户协议</a>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© 2024 珑饰 LongShi. All rights reserved.</span>
      <span>ICP备案号：浙ICP备XXXXXXXX号</span>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  background: #1A1714;
  color: rgba(255,255,255,.65);
  margin-top: auto;
}

.footer-main {
  max-width: 1320px;
  margin: 0 auto;
  padding: 56px 32px 40px;
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 48px;
}

.footer-brand {
  font-size: 22px;
  font-weight: 800;
  color: white;
  margin-bottom: 12px;
}

.footer-tagline {
  font-size: 13px;
  line-height: 1.7;
  margin-bottom: 20px;
}

.footer-socials { display: flex; gap: 10px; }
.footer-social-btn {
  width: 36px; height: 36px;
  border-radius: 8px;
  background: rgba(255,255,255,.1);
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700; color: rgba(255,255,255,.7);
  cursor: pointer;
  transition: background .15s;
}
.footer-social-btn:hover { background: rgba(255,255,255,.2); }

.footer-col h4 {
  font-size: 13px;
  font-weight: 700;
  color: white;
  margin-bottom: 16px;
  letter-spacing: .5px;
}
.footer-col a {
  display: block;
  font-size: 13px;
  color: rgba(255,255,255,.55);
  margin-bottom: 10px;
  text-decoration: none;
  transition: color .15s;
}
.footer-col a:hover { color: #C4906A; }

.footer-bottom {
  border-top: 1px solid rgba(255,255,255,.08);
  max-width: 1320px;
  margin: 0 auto;
  padding: 18px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: rgba(255,255,255,.35);
}
</style>
