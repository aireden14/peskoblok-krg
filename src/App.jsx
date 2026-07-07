import { useMemo, useState } from "react";
import {
  BadgeCheck,
  ChevronUp,
  Instagram,
  MapPin,
  MessageCircle,
  Minus,
  PackageCheck,
  Phone,
  Plus,
  ShieldCheck,
  ShoppingCart,
  Snowflake,
  Sparkles,
  Trash2,
  Truck,
  X,
} from "lucide-react";
import {
  address,
  categories,
  instagramUrl,
  phoneDisplay,
  products,
  whatsappDirectUrl,
  whatsappNumber,
} from "./products.js";

const assetUrl = (path) => `${import.meta.env.BASE_URL}${path}`;

const formatPrice = (value) =>
  new Intl.NumberFormat("ru-RU").format(value).replace(/\s/g, " ") + " тг";

function App() {
  const [activeCategory, setActiveCategory] = useState("all");
  const [cart, setCart] = useState({});
  const [cartOpen, setCartOpen] = useState(false);

  const cartItems = useMemo(
    () =>
      products
        .map((product) => ({
          ...product,
          quantity: cart[product.id] || 0,
          subtotal: product.price * (cart[product.id] || 0),
        }))
        .filter((product) => product.quantity > 0),
    [cart],
  );

  const totalQuantity = cartItems.reduce((sum, item) => sum + item.quantity, 0);
  const totalPrice = cartItems.reduce((sum, item) => sum + item.subtotal, 0);
  const filteredProducts =
    activeCategory === "all"
      ? products
      : products.filter((product) => product.category === activeCategory);

  const changeQuantity = (id, nextQuantity) => {
    setCart((current) => {
      const normalized = Math.max(0, nextQuantity);
      const next = { ...current };
      if (normalized === 0) {
        delete next[id];
      } else {
        next[id] = normalized;
      }
      return next;
    });
  };

  const buildWhatsappUrl = () => {
    const lines =
      cartItems.length === 0
        ? ["Здравствуйте! Хочу уточнить цены на пескоблок."]
        : [
            "Здравствуйте! Хочу заказать пескоблок:",
            "",
            ...cartItems.map(
              (item, index) =>
                `${index + 1}. ${item.categoryName}: ${item.title}, ${item.size} - ${item.quantity} шт x ${formatPrice(
                  item.price,
                )} = ${formatPrice(item.subtotal)}`,
            ),
            "",
            `Итого: ${totalQuantity} шт на ${formatPrice(totalPrice)}.`,
          ];

    lines.push("", "Актуальна ли цена данная?");
    return `https://wa.me/${whatsappNumber}?text=${encodeURIComponent(lines.join("\n"))}`;
  };

  const openCheckout = () => {
    if (cartItems.length === 0) {
      setCartOpen(true);
      return;
    }
    window.location.href = buildWhatsappUrl();
  };

  return (
    <main className="page-shell">
      <section className="hero">
        <div className="topbar">
          <div className="brand-lockup">
            <img
              className="brand-icon"
              src={assetUrl("brand/peskoblok-icon-128.png")}
              alt=""
              width="56"
              height="56"
            />
            <div>
              <p className="brand-kicker">Пескоблок Караганда</p>
              <h1>PESKOBLOK_KRG.09</h1>
            </div>
          </div>
          <div className="top-actions" aria-label="Социальные ссылки">
            <a className="icon-action" href={instagramUrl} aria-label="Instagram">
              <Instagram size={19} />
            </a>
            <a className="icon-action" href={whatsappDirectUrl} aria-label="WhatsApp">
              <MessageCircle size={19} />
            </a>
          </div>
        </div>

        <div className="hero-grid">
          <div className="hero-copy">
            <div className="status-pill">
              <Sparkles size={16} />
              Прайс с быстрым расчетом
            </div>
            <h2>Пескоблок из балласта и отсева</h2>
            <p>
              Выберите позиции, количество пересчитается сразу. Заказ отправится в WhatsApp
              готовым списком.
            </p>
            <div className="hero-actions">
              <a className="primary-link" href="#catalog">
                <ShoppingCart size={18} />
                Выбрать блоки
              </a>
              <a className="secondary-link" href={whatsappDirectUrl}>
                <MessageCircle size={18} />
                WhatsApp
              </a>
            </div>
          </div>

        </div>

        <div className="contact-card" aria-label="Контакты">
          <div className="contact-row">
            <Phone size={18} />
            <a href={whatsappDirectUrl}>{phoneDisplay}</a>
          </div>
          <div className="contact-row">
            <MapPin size={18} />
            <span>{address}</span>
          </div>
        </div>

        <div className="quality-strip" aria-label="Преимущества">
          <span>
            <ShieldCheck size={16} />
            Прочный бетон
          </span>
          <span>
            <Snowflake size={16} />
            Морозостойкий
          </span>
          <span>
            <Truck size={16} />
            Долговечный
          </span>
        </div>
      </section>

      <section className="catalog" id="catalog" aria-label="Каталог">
        <div className="catalog-head">
          <div>
            <p className="section-kicker">Каталог</p>
            <h2>Цены за 1 штуку</h2>
          </div>
          <button
            className="cart-chip"
            type="button"
            onClick={() => setCartOpen(true)}
            aria-label="Открыть корзину"
          >
            <ShoppingCart size={18} />
            {totalQuantity}
          </button>
        </div>

        <div className="tabs" role="tablist" aria-label="Фильтр по материалу">
          {categories.map((category) => (
            <button
              key={category.id}
              className={category.id === activeCategory ? "tab active" : "tab"}
              type="button"
              onClick={() => setActiveCategory(category.id)}
            >
              {category.label}
            </button>
          ))}
        </div>

        <div className="product-list">
          {filteredProducts.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              quantity={cart[product.id] || 0}
              onChangeQuantity={changeQuantity}
            />
          ))}
        </div>
      </section>

      <footer className="footer">
        <img src={assetUrl("brand/peskoblok-icon-64.png")} alt="" width="36" height="36" />
        <div>
          <strong>PESKOBLOK_KRG.09</strong>
          <span>{address}</span>
        </div>
      </footer>

      {totalQuantity > 0 && (
        <CartBar
          totalQuantity={totalQuantity}
          totalPrice={totalPrice}
          onOpen={() => setCartOpen(true)}
          onCheckout={openCheckout}
        />
      )}

      {cartOpen && (
        <CartSheet
          cartItems={cartItems}
          totalQuantity={totalQuantity}
          totalPrice={totalPrice}
          onClose={() => setCartOpen(false)}
          onChangeQuantity={changeQuantity}
          onClear={() => setCart({})}
          whatsappUrl={buildWhatsappUrl()}
        />
      )}
    </main>
  );
}

function ProductCard({ product, quantity, onChangeQuantity }) {
  return (
    <article className="product-card">
      <div className="product-media">
        <img src={assetUrl(product.image)} alt={product.title} />
      </div>
      <div className="product-info">
        <div className="product-meta">
          <span className={`material-badge ${product.category}`}>{product.categoryName}</span>
          <span>{product.size}</span>
        </div>
        <h3>{product.title}</h3>
        <div className="price-row">
          <strong>{formatPrice(product.price)}</strong>
          {quantity > 0 && <span>{formatPrice(product.price * quantity)}</span>}
        </div>
        <Stepper
          quantity={quantity}
          onDecrement={() => onChangeQuantity(product.id, quantity - 1)}
          onIncrement={() => onChangeQuantity(product.id, quantity + 1)}
          onAdd={() => onChangeQuantity(product.id, 1)}
        />
      </div>
    </article>
  );
}

function Stepper({ quantity, onDecrement, onIncrement, onAdd }) {
  if (quantity === 0) {
    return (
      <button className="add-button" type="button" onClick={onAdd}>
        <Plus size={18} />
        В корзину
      </button>
    );
  }

  return (
    <div className="stepper" aria-label="Количество">
      <button type="button" onClick={onDecrement} aria-label="Уменьшить количество">
        <Minus size={18} />
      </button>
      <strong>{quantity}</strong>
      <button type="button" onClick={onIncrement} aria-label="Увеличить количество">
        <Plus size={18} />
      </button>
    </div>
  );
}

function CartBar({ totalQuantity, totalPrice, onOpen, onCheckout }) {
  return (
    <div className="cart-bar" aria-live="polite">
      <button className="cart-total" type="button" onClick={onOpen}>
        <ShoppingCart size={19} />
        <span>{totalQuantity} шт</span>
        <strong>{formatPrice(totalPrice)}</strong>
        <ChevronUp size={18} />
      </button>
      <button className="checkout-button" type="button" onClick={onCheckout}>
        <MessageCircle size={18} />
        Купить
      </button>
    </div>
  );
}

function CartSheet({
  cartItems,
  totalQuantity,
  totalPrice,
  onClose,
  onChangeQuantity,
  onClear,
  whatsappUrl,
}) {
  return (
    <div className="sheet-backdrop" role="presentation" onClick={onClose}>
      <section
        className="cart-sheet"
        role="dialog"
        aria-modal="true"
        aria-label="Корзина"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="sheet-handle" />
        <div className="sheet-head">
          <div>
            <p className="section-kicker">Корзина</p>
            <h2>{totalQuantity > 0 ? `${totalQuantity} шт` : "Пока пусто"}</h2>
          </div>
          <button className="icon-action quiet" type="button" onClick={onClose} aria-label="Закрыть">
            <X size={20} />
          </button>
        </div>

        {cartItems.length === 0 ? (
          <div className="empty-state">
            <PackageCheck size={34} />
            <p>Добавьте блоки из каталога, и сайт сам посчитает итог.</p>
          </div>
        ) : (
          <>
            <div className="cart-items">
              {cartItems.map((item) => (
                <div className="cart-item" key={item.id}>
                  <img src={assetUrl(item.image)} alt="" />
                  <div>
                    <span>{item.categoryName}</span>
                    <strong>{item.title}</strong>
                    <p>{formatPrice(item.subtotal)}</p>
                  </div>
                  <Stepper
                    quantity={item.quantity}
                    onDecrement={() => onChangeQuantity(item.id, item.quantity - 1)}
                    onIncrement={() => onChangeQuantity(item.id, item.quantity + 1)}
                    onAdd={() => onChangeQuantity(item.id, 1)}
                  />
                </div>
              ))}
            </div>

            <div className="summary-card">
              <div>
                <span>Всего</span>
                <strong>{formatPrice(totalPrice)}</strong>
              </div>
              <div>
                <span>Количество</span>
                <strong>{totalQuantity} шт</strong>
              </div>
            </div>

            <div className="sheet-actions">
              <a className="whatsapp-order" href={whatsappUrl}>
                <MessageCircle size={19} />
                Купить в WhatsApp
              </a>
              <button className="clear-button" type="button" onClick={onClear}>
                <Trash2 size={18} />
              </button>
            </div>

            <p className="price-note">
              <BadgeCheck size={16} />
              В сообщение добавлен вопрос: «Актуальна ли цена данная?»
            </p>
          </>
        )}
      </section>
    </div>
  );
}

export default App;
