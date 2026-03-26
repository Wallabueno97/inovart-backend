from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List
from models import (
    Service, ServiceBase, ServiceUpdate,
    Part, PartBase, PartUpdate,
    Review, ReviewBase, ReviewUpdate,
    Appointment, AppointmentBase, AppointmentUpdate,
    AdminLogin, Admin
)
from auth import (
    verify_password, get_password_hash, create_access_token, verify_token
)
from whatsapp_notifier import send_whatsapp_notification

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize default data
async def initialize_data():
    """Initialize database with default admin, services and parts if empty"""
    try:
        # Initialize admin user
        admin_count = await db.admins.count_documents({})
        if admin_count == 0:
            admin_data = {
                "id": "admin-1",
                "email": "Walisson_bueno@hotmail.com",
                "hashedPassword": get_password_hash("fenix2026")
            }
            await db.admins.insert_one(admin_data)
            logger.info("Default admin user created for INOVART3D")

        # Check if services exist
        services_count = await db.services.count_documents({})
        if services_count == 0:
            default_services = [
                {
                    "id": "srv-1",
                    "name": "Impressão 3D Personalizada",
                    "description": "Transforme suas ideias em realidade com impressão 3D de alta qualidade",
                    "features": [
                        "Múltiplas cores disponíveis",
                        "Alta precisão e detalhamento",
                        "Diversos materiais (PLA, ABS, PETG)",
                        "Acabamento profissional"
                    ]
                },
                {
                    "id": "srv-2",
                    "name": "Modelagem 3D",
                    "description": "Criação de modelos 3D personalizados do zero",
                    "features": [
                        "Design sob medida",
                        "Modelagem técnica e artística",
                        "Otimização para impressão",
                        "Arquivos em múltiplos formatos"
                    ]
                },
                {
                    "id": "srv-3",
                    "name": "Prototipagem Rápida",
                    "description": "Desenvolvimento rápido de protótipos funcionais",
                    "features": [
                        "Entrega em 24-48h",
                        "Testes de encaixe e funcionalidade",
                        "Ajustes e refinamentos",
                        "Ideal para validação de projetos"
                    ]
                },
                {
                    "id": "srv-4",
                    "name": "Bonecos e Miniaturas",
                    "description": "Produção de action figures, miniaturas e colecionáveis personalizados",
                    "features": [
                        "Personagens e mascotes",
                        "Réplicas de personagens",
                        "Miniaturas para jogos",
                        "Acabamento e pintura (opcional)"
                    ]
                },
                {
                    "id": "srv-5",
                    "name": "Suportes e Organizadores",
                    "description": "Soluções práticas e funcionais para seu dia a dia",
                    "features": [
                        "Suportes de celular",
                        "Organizadores de mesa",
                        "Porta-objetos personalizados",
                        "Design ergonômico"
                    ]
                }
            ]
            await db.services.insert_many(default_services)
            logger.info("Default services initialized")

        # Check if parts exist
        parts_count = await db.parts.count_documents({})
        if parts_count == 0:
            default_parts = [
                {
                    "id": "part-1",
                    "name": "Boneco Personalizado",
                    "description": "Action figure personalizado em 3D com detalhamento premium",
                    "category": "Bonecos",
                    "image": "https://images.unsplash.com/photo-1772452858547-12e8781eaf27",
                    "inStock": True,
                    "price": 89.90
                },
                {
                    "id": "part-2",
                    "name": "Miniatura Decorativa",
                    "description": "Peças decorativas e miniaturas temáticas",
                    "category": "Miniaturas",
                    "image": "https://images.unsplash.com/photo-1767498051838-a08e30d1cde7",
                    "inStock": True,
                    "price": 45.00
                },
                {
                    "id": "part-3",
                    "name": "Suporte de Celular",
                    "description": "Suporte ergonômico e moderno para smartphone",
                    "category": "Suportes",
                    "image": "https://images.pexels.com/photos/4065883/pexels-photo-4065883.jpeg",
                    "inStock": True,
                    "price": 35.00
                },
                {
                    "id": "part-4",
                    "name": "Organizador de Mesa",
                    "description": "Organizador funcional com múltiplos compartimentos",
                    "category": "Organizadores",
                    "image": "https://images.unsplash.com/photo-1644463589256-02679b9c0767",
                    "inStock": True,
                    "price": 55.00
                },
                {
                    "id": "part-5",
                    "name": "Coleção de Miniaturas",
                    "description": "Set com diversas miniaturas coloridas",
                    "category": "Miniaturas",
                    "image": "https://images.unsplash.com/photo-1762829136534-aa16c1ca2f1b",
                    "inStock": True,
                    "price": 120.00
                },
                {
                    "id": "part-6",
                    "name": "Peça Decorativa Premium",
                    "description": "Peças decorativas com acabamento especial",
                    "category": "Decoração",
                    "image": "https://images.pexels.com/photos/1630140/pexels-photo-1630140.jpeg",
                    "inStock": True,
                    "price": 75.00
                }
            ]
            await db.parts.insert_many(default_parts)
            logger.info("Default parts initialized")

        # Add sample reviews
        reviews_count = await db.reviews.count_documents({})
        if reviews_count == 0:
            default_reviews = [
                {
                    "id": "rev-1",
                    "name": "Ricardo Almeida",
                    "rating": 5,
                    "comment": "Impressão 3D de altíssima qualidade! Fizeram um boneco personalizado perfeito. Recomendo muito a INOVART3D!",
                    "approved": True
                },
                {
                    "id": "rev-2",
                    "name": "Juliana Santos",
                    "rating": 5,
                    "comment": "Excelente trabalho! Os suportes ficaram incríveis e muito funcionais. Atendimento rápido e profissional!",
                    "approved": True
                },
                {
                    "id": "rev-3",
                    "name": "Felipe Costa",
                    "rating": 5,
                    "comment": "Melhor empresa de impressão 3D da região! Qualidade impecável e preço justo. Já virei cliente fiel!",
                    "approved": True
                }
            ]
            await db.reviews.insert_many(default_reviews)
            logger.info("Default reviews initialized")

    except Exception as e:
        logger.error(f"Error initializing data: {e}")

# Routes
@api_router.get("/")
async def root():
    return {"message": "INOVART3D API - Impressão & Design 3D"}

# ============ AUTH ENDPOINTS ============
@api_router.post("/auth/login")
async def login(credentials: AdminLogin):
    try:
        admin = await db.admins.find_one({"email": credentials.email})
        if not admin or not verify_password(credentials.password, admin["hashedPassword"]):
            raise HTTPException(status_code=401, detail="Email ou senha incorretos")
        
        access_token = create_access_token(data={"sub": admin["email"]})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "email": admin["email"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Erro no login")

@api_router.get("/auth/verify")
async def verify_auth(email: str = Depends(verify_token)):
    return {"authenticated": True, "email": email}

# Services endpoints
@api_router.get("/services", response_model=List[Service])
async def get_services():
    try:
        services = await db.services.find().to_list(100)
        return services
    except Exception as e:
        logger.error(f"Error fetching services: {e}")
        raise HTTPException(status_code=500, detail="Error fetching services")

@api_router.post("/services", response_model=Service)
async def create_service(service_data: ServiceBase, email: str = Depends(verify_token)):
    try:
        service = Service(**service_data.dict())
        await db.services.insert_one(service.dict())
        logger.info(f"Service created by {email}: {service.name}")
        return service
    except Exception as e:
        logger.error(f"Error creating service: {e}")
        raise HTTPException(status_code=500, detail="Error creating service")

@api_router.put("/services/{service_id}", response_model=Service)
async def update_service(service_id: str, service_data: ServiceUpdate, email: str = Depends(verify_token)):
    try:
        update_data = {k: v for k, v in service_data.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No data to update")
        
        result = await db.services.find_one_and_update(
            {"id": service_id},
            {"$set": update_data},
            return_document=True
        )
        if not result:
            raise HTTPException(status_code=404, detail="Service not found")
        
        logger.info(f"Service updated by {email}: {service_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating service: {e}")
        raise HTTPException(status_code=500, detail="Error updating service")

@api_router.delete("/services/{service_id}")
async def delete_service(service_id: str, email: str = Depends(verify_token)):
    try:
        result = await db.services.delete_one({"id": service_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Service not found")
        
        logger.info(f"Service deleted by {email}: {service_id}")
        return {"message": "Service deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting service: {e}")
        raise HTTPException(status_code=500, detail="Error deleting service")

# Parts endpoints
@api_router.get("/parts", response_model=List[Part])
async def get_parts():
    try:
        parts = await db.parts.find().to_list(100)
        return parts
    except Exception as e:
        logger.error(f"Error fetching parts: {e}")
        raise HTTPException(status_code=500, detail="Error fetching parts")

@api_router.post("/parts", response_model=Part)
async def create_part(part_data: PartBase, email: str = Depends(verify_token)):
    try:
        part = Part(**part_data.dict())
        await db.parts.insert_one(part.dict())
        logger.info(f"Part created by {email}: {part.name}")
        return part
    except Exception as e:
        logger.error(f"Error creating part: {e}")
        raise HTTPException(status_code=500, detail="Error creating part")

@api_router.put("/parts/{part_id}", response_model=Part)
async def update_part(part_id: str, part_data: PartUpdate, email: str = Depends(verify_token)):
    try:
        update_data = {k: v for k, v in part_data.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No data to update")
        
        result = await db.parts.find_one_and_update(
            {"id": part_id},
            {"$set": update_data},
            return_document=True
        )
        if not result:
            raise HTTPException(status_code=404, detail="Part not found")
        
        logger.info(f"Part updated by {email}: {part_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating part: {e}")
        raise HTTPException(status_code=500, detail="Error updating part")

@api_router.delete("/parts/{part_id}")
async def delete_part(part_id: str, email: str = Depends(verify_token)):
    try:
        result = await db.parts.delete_one({"id": part_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Part not found")
        
        logger.info(f"Part deleted by {email}: {part_id}")
        return {"message": "Part deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting part: {e}")
        raise HTTPException(status_code=500, detail="Error deleting part")

# Reviews endpoints
@api_router.get("/reviews", response_model=List[Review])
async def get_reviews():
    try:
        reviews = await db.reviews.find({"approved": True}).sort("createdAt", -1).to_list(100)
        return reviews
    except Exception as e:
        logger.error(f"Error fetching reviews: {e}")
        raise HTTPException(status_code=500, detail="Error fetching reviews")

@api_router.get("/admin/reviews", response_model=List[Review])
async def get_all_reviews(email: str = Depends(verify_token)):
    try:
        reviews = await db.reviews.find().sort("createdAt", -1).to_list(100)
        return reviews
    except Exception as e:
        logger.error(f"Error fetching all reviews: {e}")
        raise HTTPException(status_code=500, detail="Error fetching reviews")

@api_router.post("/reviews", response_model=Review)
async def create_review(review_data: ReviewBase):
    try:
        review = Review(**review_data.dict())
        await db.reviews.insert_one(review.dict())
        logger.info(f"New review created by {review.name}")
        return review
    except Exception as e:
        logger.error(f"Error creating review: {e}")
        raise HTTPException(status_code=500, detail="Error creating review")

@api_router.put("/reviews/{review_id}", response_model=Review)
async def update_review(review_id: str, review_data: ReviewUpdate, email: str = Depends(verify_token)):
    try:
        update_data = {k: v for k, v in review_data.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No data to update")
        
        result = await db.reviews.find_one_and_update(
            {"id": review_id},
            {"$set": update_data},
            return_document=True
        )
        if not result:
            raise HTTPException(status_code=404, detail="Review not found")
        
        logger.info(f"Review updated by {email}: {review_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating review: {e}")
        raise HTTPException(status_code=500, detail="Error updating review")

@api_router.delete("/reviews/{review_id}")
async def delete_review(review_id: str, email: str = Depends(verify_token)):
    try:
        result = await db.reviews.delete_one({"id": review_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Review not found")
        
        logger.info(f"Review deleted by {email}: {review_id}")
        return {"message": "Review deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting review: {e}")
        raise HTTPException(status_code=500, detail="Error deleting review")

# ============ APPOINTMENTS ENDPOINTS ============
@api_router.get("/appointments", response_model=List[Appointment])
async def get_appointments(email: str = Depends(verify_token)):
    try:
        appointments = await db.appointments.find().sort("createdAt", -1).to_list(100)
        return appointments
    except Exception as e:
        logger.error(f"Error fetching appointments: {e}")
        raise HTTPException(status_code=500, detail="Error fetching appointments")

@api_router.post("/appointments", response_model=Appointment)
async def create_appointment(appointment_data: AppointmentBase):
    try:
        appointment = Appointment(**appointment_data.dict())
        await db.appointments.insert_one(appointment.dict())
        logger.info(f"New appointment created by {appointment.customerName}")
        
        # Send WhatsApp notification
        send_whatsapp_notification(appointment.dict())
        
        return appointment
    except Exception as e:
        logger.error(f"Error creating appointment: {e}")
        raise HTTPException(status_code=500, detail="Error creating appointment")

@api_router.put("/appointments/{appointment_id}", response_model=Appointment)
async def update_appointment(appointment_id: str, appointment_data: AppointmentUpdate, email: str = Depends(verify_token)):
    try:
        update_data = {k: v for k, v in appointment_data.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No data to update")
        
        result = await db.appointments.find_one_and_update(
            {"id": appointment_id},
            {"$set": update_data},
            return_document=True
        )
        if not result:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        logger.info(f"Appointment updated by {email}: {appointment_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating appointment: {e}")
        raise HTTPException(status_code=500, detail="Error updating appointment")

@api_router.delete("/appointments/{appointment_id}")
async def delete_appointment(appointment_id: str, email: str = Depends(verify_token)):
    try:
        result = await db.appointments.delete_one({"id": appointment_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        logger.info(f"Appointment deleted by {email}: {appointment_id}")
        return {"message": "Appointment deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting appointment: {e}")
        raise HTTPException(status_code=500, detail="Error deleting appointment")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await initialize_data()
    logger.info("INOVART3D API started successfully")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("Database connection closed")
