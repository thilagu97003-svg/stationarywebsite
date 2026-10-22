(() => {
  const csrf = document.querySelector('meta[name="csrf-token"]').content;

  const post = (url, data = {}) =>
    fetch(url, {
      method: 'POST',
      headers: { 'X-CSRFToken': csrf, 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams(data),
    }).then((r) => r.json().then((j) => ({ ...j, httpOk: r.ok })));

  const toast = (text, type = '') => {
    const el = document.createElement('div');
    el.className = `toast-item ${type}`;
    el.textContent = text;
    document.getElementById('toastBox').appendChild(el);
    setTimeout(() => el.remove(), 2600);
  };

  const setCount = (n) => {
    const badge = document.getElementById('cartCount');
    badge.textContent = n;
    badge.classList.toggle('d-none', n === 0);
  };

  // Add to cart (Shop + Home cards)
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('.js-add');
    if (!btn) return;
    btn.disabled = true;
    try {
      const res = await post(btn.dataset.url);
      if (res.httpOk) { setCount(res.count); toast(res.message); }
      else toast('Could not add to cart. Try again.', 'danger');
    } catch { toast('Network error. Try again.', 'danger'); }
    finally { btn.disabled = false; }
  });

  // Cart quantity +/- (Cart page)
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('.js-qty');
    if (!btn) return;
    const row = btn.closest('tr');
    const next = Number(row.dataset.qty) + Number(btn.dataset.delta);
    if (next < 1 && !confirm('Remove this item from your cart?')) return;
    const res = await post(row.dataset.url, { qty: Math.max(next, 0) });
    if (!res.httpOk) return toast('Could not update cart.', 'danger');
    setCount(res.count);
    if (res.qty === 0) {
      row.remove();
      if (!document.querySelector('.cart-table tbody tr')) location.reload();
    } else {
      row.dataset.qty = res.qty;
      row.querySelector('.qty-val').textContent = res.qty;
      row.querySelector('.unit').textContent = res.unit_price;
      row.querySelector('.line').textContent = res.line_total;
    }
    document.querySelectorAll('#subtotal,#total').forEach((el) => (el.textContent = res.total));
  });

  // Sign-in: request OTP
  const otpBtn = document.getElementById('sendOtp');
  if (otpBtn) {
    otpBtn.addEventListener('click', async () => {
      const hint = document.getElementById('otpHint');
      const res = await post(otpBtn.dataset.url, { phone: document.getElementById('id_phone').value.trim() });
      hint.textContent = res.message;
      hint.style.color = res.httpOk ? '#0b5a0b' : '#b00020';
    });
  }
})();
