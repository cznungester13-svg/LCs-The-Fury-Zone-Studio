import { useEffect, useState, useCallback, useMemo } from "react";
import { useParams } from "react-router-dom";
import api, { imgUrl } from "@/lib/api";
import { Btn, Badge, Spinner, CONDITION_LABEL } from "@/components/common";
import { ReviewsSection } from "@/pages/ProductDetail";
import { useCart } from "@/context/CartContext";
import { useAuth } from "@/context/AuthContext";
import { toast } from "sonner";
import { ShoppingCart } from "lucide-react";

export default function ListingDetail() {
  const { id } = useParams();
  const { addToCart } = useCart();
  const { user } = useAuth();

  const [listing, setListing] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [activeImg, setActiveImg] = useState(0);
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");

  const loadReviews = useCallback(() => {
    api.get(`/reviews?target_id=${id}`).then(({ data }) => setReviews(data));
  }, [id]);

  useEffect(() => {
    api
      .get(`/listings/${id}`)
      .then(({ data }) => setListing(data))
      .catch(() => toast.error("Listing not found"));

    loadReviews();
  }, [id, loadReviews]);

  useEffect(() => {
    setActiveImg(0);
  }, [listing]);

  if (!listing) return <Spinner />;

  const sold = String(listing.status).toLowerCase() === "sold";

  const handleAdd = async () => {
    if (!user) return toast.error("Please login to buy");
    try {
      await addToCart({ item_type: "listing", item_id: listing.id, quantity: 1 });
      toast.success("Added to cart");
    } catch (e) {
      toast.error(e.response?.data?.detail || "Could not add to cart");
    }
  };

  const submitReview = async (e) => {
    e.preventDefault();
    if (!user) return toast.error("Please login");

    try {
      await api.post("/reviews", {
        target_id: id,
        target_type: "listing",
        rating,
        comment,
      });
      setComment("");
      toast.success("Review posted");
      loadReviews();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Could not post review");
    }
  };

  const reviewProps = useMemo(
    () => ({
      reviews,
      rating,
      setRating,
      comment,
      setComment,
      onSubmit: submitReview,
      user,
    }),
    [reviews, rating, comment, user]
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="grid md:grid-cols-2 gap-10">
        <div>
          <div className="border-2 border-black overflow-hidden aspect-square bg-zinc-100">
            <img
              src={listing.images?.length ? imgUrl(listing.images[activeImg]) : ""}
              alt={listing.title}
              className="w-full h-full object-cover"
              data-testid="listing-main-image"
            />
          </div>

          {listing.images?.length > 1 && (
            <div className="flex gap-3 mt-4">
              {listing.images.map((im, i) => (
                <button
                  key={i}
                  onClick={() => setActiveImg(i)}
                  className={`w-20 h-20 border-2 overflow-hidden ${
                    i === activeImg ? "border-[#FF3B30]" : "border-zinc-200"
                  }`}
                >
                  <img src={imgUrl(im)} alt="" className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          )}
        </div>

        <div>
          <div className="flex gap-2 mb-3">
            <Badge className="!bg-black !text-white !border-black">Resale</Badge>
            <Badge>{CONDITION_LABEL[listing.condition] || "Unknown"}</Badge>
          </div>

          <h1 className="text-4xl font-black uppercase tracking-tighter">{listing.title}</h1>
          <p className="font-mono uppercase text-xs tracking-widest text-zinc-500 mt-2">
            Sold by {listing.seller_name}
          </p>

          <p className="text-4xl font-black mt-5" data-testid="listing-price">
            ${Number(listing.price || 0).toFixed(2)}
          </p>

          <p className="text-zinc-600 mt-4 leading-relaxed">{listing.description}</p>

          <div className="mt-6 flex gap-3">
            <Btn
              onClick={handleAdd}
              disabled={sold}
              className="flex-1"
              data-testid="listing-add-to-cart-btn"
            >
              <ShoppingCart size={18} /> {sold ? "Sold" : "Add to cart"}
            </Btn>
          </div>

          {sold && (
            <p className="text-[#FF3B30] font-bold mt-3 uppercase">This item has been sold.</p>
          )}
        </div>
      </div>

      <ReviewsSection {...reviewProps} />
    </div>
  );
}
