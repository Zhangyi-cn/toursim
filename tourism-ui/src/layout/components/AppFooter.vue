<template>
  <footer class="footer">
    <div class="footer-content">
      <div class="footer-main">
        <div class="footer-logo">
          <div class="logo">
            <svg viewBox="0 0 500 500" width="40" height="40">
              <defs>
                <linearGradient id="footer-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" style="stop-color:#4481eb;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#04befe;stop-opacity:1" />
                </linearGradient>
              </defs>
              <path fill="url(#footer-gradient)" d="M482.207,187.088c0-1.862-0.822-3.612-2.231-4.785c-1.409-1.173-3.259-1.718-5.073-1.492L365.412,199.92
                l-96.859-132.837c-0.99-1.356-2.534-2.222-4.262-2.358c-1.728-0.136-3.422,0.454-4.629,1.619l-32.358,31.277l-32.358-31.277
                c-1.207-1.165-2.901-1.756-4.629-1.619c-1.728,0.136-3.271,1.002-4.262,2.358L89.197,199.92L-19.294,180.81
                c-1.813-0.227-3.663,0.319-5.073,1.492c-1.409,1.173-2.231,2.923-2.231,4.785v106.928c0,2.255,1.359,4.292,3.44,5.157
                l160.959,66.927c0.979,0.407,2.02,0.611,3.061,0.611c1.041,0,2.082-0.204,3.061-0.611l160.959-66.927
                c2.081-0.865,3.44-2.902,3.44-5.157V187.088z" />
            </svg>
            <h2 class="logo-text">Travel<span>Joy</span></h2>
          </div>
          <p class="slogan">旅游平台致力于为用户提供优质的旅游服务，让每一次旅行都充满美好回忆。</p>
          <div class="social-links">
            <a href="#" class="social-link">
              <el-icon><Platform /></el-icon>
            </a>
            <a href="#" class="social-link">
              <el-icon><ChatDotSquare /></el-icon>
            </a>
            <a href="#" class="social-link">
              <el-icon><Share /></el-icon>
            </a>
          </div>
        </div>

        <div class="footer-links">
          <div class="links-group">
            <h3>快速链接</h3>
            <ul>
              <li><a href="/attractions">景点</a></li>
              <li><a href="/notes">游记</a></li>
              <li><a href="/about">关于我们</a></li>
              <li><a href="/contact">联系我们</a></li>
            </ul>
          </div>

          <div class="links-group">
            <h3>联系我们</h3>
            <ul>
              <li>
                <el-icon><Phone /></el-icon>
                <span>400-123-4567</span>
              </li>
              <li>
                <el-icon><Message /></el-icon>
                <span>support@tourism.com</span>
              </li>
              <li>
                <el-icon><Location /></el-icon>
                <span>北京市朝阳区三里屯SOHO</span>
              </li>
            </ul>
          </div>

          <div class="links-group qrcode-group">
            <h3>关注我们</h3>
            <div class="qrcode">
              <img src="/placeholder-image.jpg" alt="微信二维码">
              <p>扫码关注公众号</p>
            </div>
          </div>
        </div>
      </div>

      <div class="footer-bottom">
        <div class="copyright">
          <p>© 2025 TravelJoy. All Rights Reserved.</p>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { Platform, ChatDotSquare, Share, Location, Message, Phone } from '@element-plus/icons-vue'
</script>

<style lang="scss" scoped>
.footer {
  background: linear-gradient(135deg, #1abc9c, #16a085);
  color: #fff;
  padding: 100px 0 40px;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  }

  .footer-content {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 30px;

    .footer-main {
      display: grid;
      grid-template-columns: 1.2fr 2fr;
      gap: 80px;
      margin-bottom: 80px;

      .footer-logo {
        .logo {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 30px;
          
          svg {
            filter: drop-shadow(0 4px 8px rgba(0,0,0,0.15));
            transition: all 0.3s ease;
            
            &:hover {
              transform: rotate(15deg);
            }
          }

          .logo-text {
            font-size: 28px;
            font-weight: 800;
            color: #fff;
            letter-spacing: 0.5px;

            span {
              font-weight: 400;
              opacity: 0.9;
            }
          }
        }

        .slogan {
          font-size: 16px;
          line-height: 1.8;
          color: rgba(255,255,255,0.9);
          margin-bottom: 40px;
          text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .social-links {
          display: flex;
          gap: 20px;

          .social-link {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: rgba(255,255,255,0.15);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);

            &:hover {
              background: #fff;
              transform: translateY(-5px);
              color: #1abc9c;
              box-shadow: 0 10px 20px rgba(0,0,0,0.1);

              .el-icon {
                transform: scale(1.1);
              }
            }

            .el-icon {
              font-size: 22px;
              transition: all 0.3s ease;
            }
          }
        }
      }

      .footer-links {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 60px;

        .links-group {
          h3 {
            font-size: 20px;
            font-weight: 600;
            color: #fff;
            margin-bottom: 30px;
            position: relative;
            padding-bottom: 15px;
            letter-spacing: 0.5px;

            &::after {
              content: '';
              position: absolute;
              left: 0;
              bottom: 0;
              width: 40px;
              height: 3px;
              background: rgba(255,255,255,0.3);
              border-radius: 2px;
              transition: all 0.3s ease;
            }

            &:hover::after {
              width: 60px;
              background: #fff;
            }
          }

          ul {
            list-style: none;
            padding: 0;

            li {
              margin-bottom: 20px;
              display: flex;
              align-items: center;
              gap: 12px;

              a {
                color: rgba(255,255,255,0.9);
                text-decoration: none;
                transition: all 0.3s ease;
                font-size: 16px;
                position: relative;
                padding-bottom: 2px;

                &::after {
                  content: '';
                  position: absolute;
                  left: 0;
                  bottom: 0;
                  width: 0;
                  height: 1px;
                  background: #fff;
                  transition: all 0.3s ease;
                }

                &:hover {
                  color: #fff;
                  transform: translateX(5px);

                  &::after {
                    width: 100%;
                  }
                }
              }

              .el-icon {
                color: rgba(255,255,255,0.9);
                font-size: 20px;
                transition: all 0.3s ease;
              }

              span {
                color: rgba(255,255,255,0.9);
                font-size: 16px;
                transition: all 0.3s ease;
              }

              &:hover {
                .el-icon {
                  color: #fff;
                  transform: scale(1.1);
                }
                span {
                  color: #fff;
                }
              }
            }
          }

          &.qrcode-group {
            .qrcode {
              background: rgba(255,255,255,0.15);
              padding: 24px;
              border-radius: 16px;
              text-align: center;
              backdrop-filter: blur(5px);
              transition: all 0.3s ease;

              &:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);
                background: rgba(255,255,255,0.2);

                img {
                  transform: scale(1.05);
                }
              }

              img {
                width: 140px;
                height: 140px;
                border-radius: 12px;
                margin-bottom: 16px;
                transition: all 0.3s ease;
              }

              p {
                font-size: 15px;
                color: rgba(255,255,255,0.9);
                font-weight: 500;
              }
            }
          }
        }
      }
    }

    .footer-bottom {
      padding-top: 40px;
      border-top: 1px solid rgba(255,255,255,0.15);

      .copyright {
        text-align: center;
        color: rgba(255,255,255,0.8);
        font-size: 15px;
        
        p {
          transition: all 0.3s ease;
          
          &:hover {
            color: #fff;
            transform: translateY(-2px);
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .footer {
    padding: 60px 0 30px;

    .footer-content {
      .footer-main {
        grid-template-columns: 1fr;
        gap: 40px;
        margin-bottom: 40px;

        .footer-links {
          grid-template-columns: 1fr;
          gap: 30px;

          .links-group {
            &.qrcode-group {
              .qrcode {
                img {
                  width: 120px;
                  height: 120px;
                }
              }
            }
          }
        }
      }
    }
  }
}
</style> 