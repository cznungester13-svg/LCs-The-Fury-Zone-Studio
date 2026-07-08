import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api, { imgUrl } from "@/lib/api";
import { Btn, Stars, Badge, Spinner } from "@/components/common";
import { useCart } from "@/context/CartContext";
import { useAuth } from "@/context/AuthContext";
import { toast } from "sonner";
import { Heart, ShoppingCart } from "lucide-react";

export default function ProductDetail() {
  const { id } = useParams();
  const { addToCart } = useCart();
  const { user } = useAuth();

  const [product, setProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [activeImg, setActiveImg] = useState(0);
  const [variant, setVariant] = useState(null);
  const [qty, setQty] = useState(1);
  const [wished, setWished] = useState(false);
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");

  const loadReviews = () =>
    api.get(`/reviews?target_id=${id}`).then(({ data }) => setReviews(data));

  // Load product + reviews
  useEffect(() => {
    api.get(`/products/${id}`).then(({ data }) => {
      setProduct(data);
      if (data.variants?.length) setVariant(data.variants[0]);
    });
    loadReviews();
  }, [id]);

  // Load initial wishlist status
  useEffect(() => {
    if (!user) return;
    api
      .get(`/wishlist/status?item_type=product&item_id=${id}`)
      .then(({ data }) => setWished(data.wishlisted));
  }, [id, user]);

  if (!product) return <Spinner />;

  const price = variant?.price ?? product.price;
  const soldOut = product.stock <= 0;

  const handleAdd = async () => {
    if (!user) return toast.error("Please login to add to cart");
    await addToCart({
      item_type: "product",
      item_id: product.id,
      quantity: qty,
      variant_id: variant?.id,
    });
    toast.success("Added to cart");
  };

  const toggleWish = async () => {
    if (!user) return toast.error("Please login");
    const { data } = await api.post("/wishlist/toggle", {
      item_type: "product",
      item_id: product.id,
    });
    setWished(data.wishlisted);
    toast.success(
      data.wishlisted ? "Added to wishlist" : "Removed from wishlist"
    );
  };

  const submitReview = async (e) => {
    e.preventDefault();
    if (!user) return toast.error("Please login to review");
    await api.post("/reviews", {
      target_id: id,
      target_type: "product",
      rating,
      comment,
    });
    setComment("");
    setRating(5);
    toast.success("Review posted");
    loadReviews();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* ...rest of your JSX stays exactly the same... */}
    </div>
  );
}
