import React, { useMemo, useState } from 'react';
import { ShoppingCart, Search, Star } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

const products = [
  { id: 1, name: 'Luxury Chocolate Hamper', price: 29.99, rating: 5 },
  { id: 2, name: 'Birthday Surprise Box', price: 24.99, rating: 5 },
  { id: 3, name: 'Personalised Mug Set', price: 19.99, rating: 4 },
  { id: 4, name: 'Scottish Treat Basket', price: 34.99, rating: 5 },
];

export default function AberdeenGiftShop() {
  const [query, setQuery] = useState('');
  const [cart, setCart] = useState([] as any[]);

  const filtered = useMemo(() => products.filter(p => p.name.toLowerCase().includes(query.toLowerCase())), [query]);
  const total = cart.reduce((sum, item) => sum + item.price, 0);

  const addToCart = (product:any) => setCart([...cart, product]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="sticky top-0 z-50 bg-slate-900 text-white shadow">
        <div className="max-w-6xl mx-auto flex items-center justify-between p-4">
          <h1 className="text-2xl font-bold">Aberdeen Gift Shop</h1>
          <div className="flex items-center gap-3">
            <div className="relative hidden md:block">
              <Search className="absolute left-3 top-3 h-4 w-4" />
              <Input className="pl-10 w-72 bg-white text-black" placeholder="Search gifts..." value={query} onChange={e => setQuery(e.target.value)} />
            </div>
            <Button variant="secondary" className="gap-2">
              <ShoppingCart className="h-4 w-4" /> {cart.length}
            </Button>
          </div>
        </div>
      </header>

      <section className="max-w-6xl mx-auto grid md:grid-cols-2 gap-8 p-6 items-center">
        <div>
          <h2 className="text-5xl font-bold mb-4">Premium Gifts with Free Aberdeen Delivery</h2>
          <p className="text-lg text-slate-600 mb-6">Luxury hampers, birthday presents and personalised gifts delivered locally.</p>
          <Button size="lg">Shop Now</Button>
        </div>
        <Card className="rounded-2xl shadow-xl"><CardContent className="p-8 text-center"><p className="text-xl font-semibold">Same Day Delivery Available</p></CardContent></Card>
      </section>

      <section className="max-w-6xl mx-auto p-6">
        <h3 className="text-3xl font-bold mb-6">Best Sellers</h3>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {filtered.map(product => (
            <Card key={product.id} className="rounded-2xl shadow hover:shadow-lg transition">
              <CardContent className="p-5 space-y-3">
                <div className="h-40 rounded-xl bg-slate-200" />
                <h4 className="font-semibold">{product.name}</h4>
                <div className="flex gap-1">{Array.from({length: product.rating}).map((_,i)=><Star key={i} className="h-4 w-4 fill-current" />)}</div>
                <p className="text-lg font-bold">£{product.price.toFixed(2)}</p>
                <Button className="w-full" onClick={() => addToCart(product)}>Add to Cart</Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section className="max-w-6xl mx-auto p-6 grid md:grid-cols-2 gap-6">
        <Card className="rounded-2xl"><CardContent className="p-6"><h3 className="text-2xl font-bold mb-4">Your Basket</h3>{cart.length===0?<p>No items yet.</p>:cart.map((item,i)=><p key={i}>{item.name} - £{item.price.toFixed(2)}</p>)}<p className="mt-4 font-bold">Total: £{total.toFixed(2)}</p></CardContent></Card>
        <Card className="rounded-2xl"><CardContent className="p-6"><h3 className="text-2xl font-bold mb-4">Secure Checkout</h3><div className="space-y-3"><Input placeholder="Full Name" /><Input placeholder="Email" /><Input placeholder="Address" /><Input placeholder="Card Number" /><Button className="w-full">Place Order</Button></div></CardContent></Card>
      </section>

      <footer className="bg-slate-900 text-white mt-10">
        <div className="max-w-6xl mx-auto p-6 text-center">© 2026 Aberdeen Gift Shop • Free Local Delivery</div>
      </footer>
    </div>
  );
}
