import os
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "local-demo-key-change-me")
db_url = os.getenv("DATABASE_URL", "sqlite:///hoa_demo.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class WorkOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, default="")
    location = db.Column(db.String(160), default="")
    priority = db.Column(db.String(30), default="Normal")
    status = db.Column(db.String(40), default="New")
    requester = db.Column(db.String(100), default="Resident")
    vendor = db.Column(db.String(120), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    trade = db.Column(db.String(80), default="")
    insured = db.Column(db.Boolean, default=True)
    active = db.Column(db.Boolean, default=True)

class Audit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entity = db.Column(db.String(40), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(200), nullable=False)
    actor = db.Column(db.String(80), default="System")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    resident = db.Column(db.String(100), default="")
    category = db.Column(db.String(80), default="Exterior modification")
    status = db.Column(db.String(40), default="Submitted")
    details = db.Column(db.Text, default="")

class BoardItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    category = db.Column(db.String(80), default="Decision")
    status = db.Column(db.String(40), default="Pending")
    details = db.Column(db.Text, default="")

def log(entity, entity_id, action, actor="Manager"):
    db.session.add(Audit(entity=entity, entity_id=entity_id, action=action, actor=actor))

def seed():
    if Vendor.query.count() == 0:
        db.session.add_all([
            Vendor(name="Summit Gate & Access", trade="Gate systems", insured=True),
            Vendor(name="Evergreen Grounds", trade="Landscaping", insured=True),
            Vendor(name="ClearFlow Plumbing", trade="Plumbing", insured=True),
            Vendor(name="BluePeak Pool Services", trade="Pool maintenance", insured=True)])
    if WorkOrder.query.count() == 0:
        items = [
            WorkOrder(title="North entrance gate not closing", description="Gate stops before fully closing; please inspect the sensor.", location="North entrance", priority="High", status="Assigned", requester="Jordan Lee", vendor="Summit Gate & Access"),
            WorkOrder(title="Streetlight out near walking trail", description="Light pole 7 is not illuminated after dusk.", location="Walking trail · Pole 7", priority="Normal", status="In Progress", requester="Taylor Morgan", vendor="Evergreen Grounds"),
            WorkOrder(title="Pool pump inspection", description="Routine equipment inspection and service.", location="Community pool", priority="Normal", status="New", requester="Casey Brooks")]
        db.session.add_all(items)
    if Review.query.count() == 0:
        db.session.add_all([
            Review(title="Backyard fence replacement", resident="Alex Rivera", category="Fence", status="Under Review", details="Replace existing fence; plans and photos received."),
            Review(title="Patio cover installation", resident="Jordan Lee", category="Exterior addition", status="Submitted", details="Site plan and contractor estimate attached.")])
    if BoardItem.query.count() == 0:
        db.session.add_all([
            BoardItem(title="North gate modernization", category="Capital project", status="Pending", details="Review vendor proposals and funding options."),
            BoardItem(title="Landscape services renewal", category="Contract", status="In Discussion", details="Compare annual service scope and pricing.")])
    db.session.commit()

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.get("/api/bootstrap")
def bootstrap():
    orders = WorkOrder.query.order_by(WorkOrder.created_at.desc()).all()
    vendors = Vendor.query.filter_by(active=True).order_by(Vendor.name).all()
    reviews = Review.query.order_by(Review.id.desc()).all()
    board = BoardItem.query.order_by(BoardItem.id.desc()).all()
    audits = Audit.query.order_by(Audit.created_at.desc()).limit(30).all()
    return jsonify({
        "community":{"name":"Canyon Ridge HOA","homes":286,"amenities":["Pool","Clubhouse","Gated entrances","Walking trails"]},
        "metrics":{"open":WorkOrder.query.filter(WorkOrder.status.notin_(["Completed","Closed"])).count(),"new":WorkOrder.query.filter_by(status="New").count(),"vendors":len(vendors),"reviews":Review.query.filter(Review.status.notin_(["Approved","Rejected"])).count()},
        "workOrders":[{"id":x.id,"title":x.title,"description":x.description,"location":x.location,"priority":x.priority,"status":x.status,"requester":x.requester,"vendor":x.vendor,"created":x.created_at.strftime("%b %d")} for x in orders],
        "vendors":[{"id":x.id,"name":x.name,"trade":x.trade,"insured":x.insured} for x in vendors],
        "reviews":[{"id":x.id,"title":x.title,"resident":x.resident,"category":x.category,"status":x.status,"details":x.details} for x in reviews],
        "board":[{"id":x.id,"title":x.title,"category":x.category,"status":x.status,"details":x.details} for x in board],
        "audit":[{"entity":x.entity,"entity_id":x.entity_id,"action":x.action,"actor":x.actor,"when":x.created_at.strftime("%b %d · %I:%M %p")} for x in audits]})

@app.post("/api/work-orders")
def create_work_order():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify(error="A request title is required."), 400
    item = WorkOrder(title=title[:160], description=(data.get("description") or "")[:2000], location=(data.get("location") or "Community")[:160], priority=data.get("priority") if data.get("priority") in ["Low","Normal","High","Urgent"] else "Normal", requester=(data.get("requester") or "Resident")[:100])
    db.session.add(item); db.session.flush()
    log("Work order", item.id, "Resident submitted a service request", item.requester)
    db.session.commit()
    return jsonify(id=item.id, message="Request submitted."), 201

@app.patch("/api/work-orders/<int:item_id>")
def update_work_order(item_id):
    item = db.session.get(WorkOrder, item_id)
    if not item: return jsonify(error="Work order not found."), 404
    data = request.get_json(silent=True) or {}
    if "vendor" in data:
        vendor = Vendor.query.filter_by(name=data["vendor"], active=True, insured=True).first()
        if not vendor: return jsonify(error="Choose an active vendor with verified insurance."), 400
        item.vendor = vendor.name
        if item.status == "New": item.status = "Assigned"
        log("Work order", item.id, f"Assigned to {vendor.name}")
    if "status" in data:
        allowed = ["New","Assigned","Scheduled","In Progress","Pending Verification","Completed","Closed"]
        if data["status"] not in allowed: return jsonify(error="Invalid status."), 400
        item.status = data["status"]
        log("Work order", item.id, f"Status changed to {item.status}", data.get("actor","Manager"))
    db.session.commit()
    return jsonify(message="Work order updated.")

@app.post("/api/reviews/<int:item_id>/decision")
def review_decision(item_id):
    item = db.session.get(Review, item_id)
    if not item: return jsonify(error="Review not found."), 404
    decision = (request.get_json(silent=True) or {}).get("decision")
    if decision not in ["Approved","Rejected","More Information Required"]: return jsonify(error="Invalid decision."), 400
    item.status = decision
    log("Architectural review", item.id, f"Decision: {decision}")
    db.session.commit()
    return jsonify(message="Review decision saved.")

@app.post("/api/board/<int:item_id>/decision")
def board_decision(item_id):
    item = db.session.get(BoardItem, item_id)
    if not item: return jsonify(error="Board item not found."), 404
    decision = (request.get_json(silent=True) or {}).get("decision")
    if decision not in ["Approved","Rejected","In Discussion"]: return jsonify(error="Invalid decision."), 400
    item.status = decision
    log("Board item", item.id, f"Board status: {decision}", "Board")
    db.session.commit()
    return jsonify(message="Board item updated.")

@app.post("/api/vendors")
def add_vendor():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name: return jsonify(error="Vendor name is required."), 400
    vendor = Vendor(name=name[:120], trade=(data.get("trade") or "General")[:80], insured=bool(data.get("insured", False)))
    db.session.add(vendor); db.session.flush()
    log("Vendor", vendor.id, "Vendor added")
    db.session.commit()
    return jsonify(message="Vendor added."), 201

with app.app_context():
    db.create_all()
    seed()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)
