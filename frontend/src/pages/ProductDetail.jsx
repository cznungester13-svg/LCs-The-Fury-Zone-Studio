import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api, { imgUrl } from "@/lib/api";
import { Btn, Badge, Spinner } from "@/components/common";
import { useCart } from "@/context/CartContext";
import { useAuth } from "@/context/AuthContext";
import { toast } from "sonner";
import { Heart, ShoppingCart } from "lucide-react";

// Dedicated Reviews UI Section inside the same file or exported
export function ReviewsSection({ reviews, rating, setRating, comment, setComment, onSubmit, user }) {
  return (
    <div className="mt-12 border-t border-zinc-200 pt-10">
      <h2 className="text-2xl font-black uppercase tracking-tight mb-6">Customer Reviews ({reviews.length})</h2>
      
      {user ? (
        <form onSubmit={onSubmit} className="mb-8 bg-zinc-50 p-6 border border-zinc-200">
          <h3 className="font-bold uppercase text-sm mb-4">Leave a Review</h3>
          <div className="flex gap-2 mb-4">
            {[1, 2, 3, 4, 5].map((num) => (
              <button
                type="button"
                key={num}
                onClick={() => setRating(num)}
                className={`text-xl ${num <= rating ? "text-yellow-500" : "text-zinc-300"}`}
              >
                ★
              </button>
            ))}
          </div>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Write your review here..."
            className="w-full p-3 border border-zinc-300 focus:outline-none focus:border-black min-h-[100px] bg-white text-sm"
            required
          />
          <Btn type="submit" className="mt-3 text-xs uppercase tracking-wider">Submit Review</Btn>
        </form>
      ) : (
        <p className="text-zinc-500 text-sm italic mb-8">Please login to write a review.</p>
      )}

      <div className="space-y-4">
        {reviews.length === 0 ? (
          <p className="text-zinc-500 text-sm">No reviews yet. Be the first to review this product!</p>
        ) : (
          reviews.map((rev) => (
            <div key={rev.id} className="border-b border-zinc-100 pb-4">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-yellow-500">{"★".repeat(rev.rating)}</span>
                <span className="font-mono text-xs text-zinc-400">by {rev.user_name || "Anonymous"}</span>
              </div>
              <p className="text-zinc-700 text-sm">{rev.comment}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default function ProductDetail() {
  const { id } = useParams();
  const { addToCart } = useCart();
  const { user } = useAuth();
  
  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [inWishlist, setInWishlist] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadReviews = () => {
    api.get(`/reviews?target_id=${id}&target_type=product`)
      .then(({ data }) => setReviews(data))
      .catch((err) => console.error("Failed to load reviews", err));
  };

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.get(`/products/${id}`),
      api.get(`/wishlist/check/${id}`).catch(() => ({ data: { in_wishlist: false } }))
    ])
      .then(([{ data: prodData }, { data: wishData }]) => {
        setProduct(prodData);
        setInWishlist(wishData.in_wishlist);
      })
      .catch((err) => {
        toast.error("Could not fetch product details");
        console.error(err);
      })
      .finally(() => setLoading(false));

    loadReviews();
  }, [id]);

  const handleAddToCart = async () => {
    if (!user) return toast.error("Please login to purchase items");
    try {
      await addToCart({ item_type: "product", item_id: product.id, quantity: 1 });
      toast.success("Added to cart");
    } catch (e) {
      toast.error(e.response?.data?.detail || "Could not add to cart");
    }
  };

  const toggleWishlist = async () => {
    if (!user) return toast.error("Please login to use your wishlist");
    try {
      if (inWishlist) {
        await api.delete(`/wishlist/${id}`);
        setInWishlist(false);
        toast.success("Removed from wishlist");
      } else {
        await api.post(`/wishlist`, { product_id: id });
        setInWishlist(true);
        toast.success("Added to wishlist");
      }
    } catch (e) {
      toast.error("Failed to update wishlist");
    }
  };

  const submitReview = async (e) => {
    e.preventDefault();
    if (!user) return toast.error("Please login to submit a review");
    if (!comment.trim()) return toast.error("Review comment cannot be empty");

    try {
      await api.post("/reviews", { 
        target_id: id, 
        target_type: "product", 
        rating, 
        comment: comment.trim() 
      });
      setComment("");
      setRating(5);
      toast.success("Review posted successfully!");
      loadReviews();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Failed to post review");
    }
  };

  if (loading) return <Spinner />;
  if (!product) return <div className="text-center py-20 font-bold uppercase">Product Not Found</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="grid md:grid-cols-2 gap-10">
        <div className="border-2 border-black overflow-hidden aspect-square bg-zinc-100">
          <img 
            src={product.image ? imgUrl(product.image) : "/placeholder-product.jpg"} 
            alt={product.name} 
            className="w-full h-full object-cover" 
          />
        </div>

        <div>
          <h1 className="text-4xl font-black uppercase tracking-tighter">{product.name}</h1>
          <p className="text-4xl font-black mt-5">${Number(product.price || 0).toFixed(2)}</p>
          <p className="text-zinc-600 mt-4 leading-relaxed">{product.description}</p>

          <div className="mt-6 flex gap-3">
            <Btn onClick={handleAddToCart} className="flex-1">
              <ShoppingCart size={18} /> Add to cart
            </Btn>
            <button 
              onClick={toggleWishlist}
              className={`p-3 border-2 border-black transition-colors ${inWishlist ? 'bg-black text-white' : 'bg-white text-black hover:bg-zinc-100'}`}
              aria-label="Toggle Wishlist"
            >
              <Heart size={20} fill={inWishlist ? "currentColor" : "none"} />
            </button>
          </div>
        </div>
      </div>

      <ReviewsSection 
        reviews={reviews} 
        rating={rating} 
        setRating={setRating} 
        comment={comment} 
        setComment={setComment} 
        onSubmit={submitReview} 
        user={user} 
      />
    </div>
  );
}
