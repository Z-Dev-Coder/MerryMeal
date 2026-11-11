import math

class GeoService:
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """
        Compute Great-Circle Distance using Haversine formula
        """
        if not lat1 or not lon1 or not lat2 or not lon2:
            return 0.0
            
        R = 6371.0 # Earth's radius in kilometers
        
        phi1 = math.radians(float(lat1))
        phi2 = math.radians(float(lat2))
        
        delta_phi = math.radians(float(lat2) - float(lat1))
        delta_lambda = math.radians(float(lon2) - float(lon1))
        
        a = (math.sin(delta_phi / 2.0) ** 2 +
             math.cos(phi1) * math.cos(phi2) *
             (math.sin(delta_lambda / 2.0) ** 2))
             
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return round(R * c, 2) # Distance in km

    @classmethod
    def get_route_details(cls, origin_lat, origin_lon, dest_lat, dest_lon):
        """
        Calculates distance details and determines service type eligibility.
        """
        distance = cls.calculate_distance(origin_lat, origin_lon, dest_lat, dest_lon)
        return {
            'distance_km': distance,
            'duration_min': math.ceil(distance * 2.5), # Estimated travel time
            'is_hot_meal_eligible': distance < 10.0
        }
