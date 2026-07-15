@router.get("/metrics")
async def metrics(admin=Depends(require_roles("admin"))):
    # Optimize Revenue via Native Database Aggregation
    pipeline = [
        {"$match": {"status": {"$nin": ["refunded", "cancelled"]}}},
        {"$group": {"_id": None, "total_revenue": {"$sum": "$total"}}}
    ]
    revenue_cursor = await db.orders.aggregate(pipeline).to_list(1)
    revenue = revenue_cursor[0]["total_revenue"] if revenue_cursor else 0.0

    # Optimize Commissions via Native Database Aggregation
    comm_pipeline = [
        {"$group": {"_id": None, "total_comm": {"$sum": "$commission"}}}
    ]
    comm_cursor = await db.commissions.aggregate(comm_pipeline).to_list(1)
    commissions = comm_cursor[0]["total_comm"] if comm_cursor else 0.0

    # Return the combined metrics
    return {
        "revenue": revenue,
        "commissions": commissions,
        "timestamp": now_iso()
    }
