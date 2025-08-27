import FreeCAD
import FreeCADGui
import re
from typing import Dict, List, Any, Optional, Tuple

class ParametricObjectManager:
    """Manager for creating parametric objects with variables and constraints"""
    
    def __init__(self, document=None):
        self.doc = document or FreeCAD.ActiveDocument
        if not self.doc:
            self.doc = FreeCAD.newDocument()
        
        self.spreadsheet = self._get_or_create_spreadsheet()
        self.variable_counter = self._get_next_variable_counter()
    
    def _get_or_create_spreadsheet(self):
        """Get existing VibeDesign spreadsheet or create new one"""
        # Look for existing VibeDesign spreadsheet
        for obj in self.doc.Objects:
            if hasattr(obj, 'TypeId') and obj.TypeId == 'Spreadsheet::Sheet':
                if obj.Name.startswith('VibeDesign_Params') or obj.Label.startswith('VibeDesign Parameters'):
                    return obj
        
        # Create new spreadsheet
        spreadsheet = self.doc.addObject('Spreadsheet::Sheet', 'VibeDesign_Params')
        spreadsheet.Label = 'VibeDesign Parameters'
        
        # Set up header row
        spreadsheet.set('A1', 'Variable')
        spreadsheet.set('B1', 'Value')
        spreadsheet.set('C1', 'Unit')
        spreadsheet.set('D1', 'Description')
        
        # Style header
        spreadsheet.setStyle('A1:D1', 'bold', 'add')
        
        return spreadsheet
    
    def _get_next_variable_counter(self):
        """Get the next available variable counter"""
        counter = 1
        if hasattr(self.spreadsheet, 'getUsedCells'):
            used_cells = self.spreadsheet.getUsedCells()
            for cell in used_cells:
                if cell.startswith('A') and cell != 'A1':
                    try:
                        row = int(cell[1:])
                        if row > counter:
                            counter = row
                    except ValueError:
                        continue
        return counter + 1
    
    def create_variable(self, name: str, value: float, unit: str = 'mm', description: str = '') -> str:
        """Create a new variable in the spreadsheet"""
        # Sanitize variable name
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        clean_name = clean_name.strip('_')
        if not clean_name or clean_name[0].isdigit():
            clean_name = f"var_{clean_name}"
        
        # Ensure unique name
        original_name = clean_name
        counter = 1
        while self._variable_exists(clean_name):
            clean_name = f"{original_name}_{counter}"
            counter += 1
        
        # Add to spreadsheet
        row = self.variable_counter
        self.spreadsheet.set(f'A{row}', clean_name)
        self.spreadsheet.set(f'B{row}', str(value))
        self.spreadsheet.set(f'C{row}', unit)
        self.spreadsheet.set(f'D{row}', description)
        
        # Set alias for the value cell so it can be referenced by name
        try:
            self.spreadsheet.setAlias(f'B{row}', clean_name)
        except Exception as e:
            FreeCAD.Console.PrintWarning(f"Could not create alias {clean_name}: {str(e)}\n")
        
        self.variable_counter += 1
        
        # Return the spreadsheet reference using the alias
        return f"{self.spreadsheet.Name}.{clean_name}"
    
    def _variable_exists(self, name: str) -> bool:
        """Check if variable already exists"""
        if not hasattr(self.spreadsheet, 'getUsedCells'):
            return False
        
        used_cells = self.spreadsheet.getUsedCells()
        for cell in used_cells:
            if cell.startswith('A') and cell != 'A1':
                try:
                    value = self.spreadsheet.get(cell)
                    if value == name:
                        return True
                except:
                    continue
        return False
    
    def create_parametric_box(self, name: str, dimensions: Dict[str, float], 
                             position: Dict[str, float] = None, 
                             rotation: Dict[str, float] = None) -> Tuple[Any, Dict[str, str]]:
        """Create a parametric box with variables"""
        
        # Default values
        position = position or {'x': 0, 'y': 0, 'z': 0}
        rotation = rotation or {'x': 0, 'y': 0, 'z': 0}
        
        # Create variables for dimensions
        variables = {}
        length = dimensions.get('length', 10)
        width = dimensions.get('width', length)  
        height = dimensions.get('height', length)
        
        variables['length'] = self.create_variable(
            f"{name}_length", length, 'mm', f'Length of {name}'
        )
        variables['width'] = self.create_variable(
            f"{name}_width", width, 'mm', f'Width of {name}'
        )
        variables['height'] = self.create_variable(
            f"{name}_height", height, 'mm', f'Height of {name}'
        )
        
        # Create position variables if not at origin
        if any(position.values()):
            variables['pos_x'] = self.create_variable(
                f"{name}_x", position['x'], 'mm', f'X position of {name}'
            )
            variables['pos_y'] = self.create_variable(
                f"{name}_y", position['y'], 'mm', f'Y position of {name}'
            )
            variables['pos_z'] = self.create_variable(
                f"{name}_z", position['z'], 'mm', f'Z position of {name}'
            )
        
        # Create the box object
        obj = self.doc.addObject("Part::Box", name)
        
        # Set parametric expressions
        obj.setExpression('Length', variables['length'])
        obj.setExpression('Width', variables['width'])
        obj.setExpression('Height', variables['height'])
        
        # Set position if not at origin
        if any(position.values()):
            obj.setExpression('Placement.Base.x', variables['pos_x'])
            obj.setExpression('Placement.Base.y', variables['pos_y'])
            obj.setExpression('Placement.Base.z', variables['pos_z'])
        else:
            obj.Placement.Base = FreeCAD.Vector(0, 0, 0)
        
        # Set rotation if specified
        if any(rotation.values()):
            obj.Placement.Rotation = FreeCAD.Rotation(rotation['x'], rotation['y'], rotation['z'])
        
        return obj, variables
    
    def create_parametric_cylinder(self, name: str, dimensions: Dict[str, float], 
                                  position: Dict[str, float] = None, 
                                  rotation: Dict[str, float] = None) -> Tuple[Any, Dict[str, str]]:
        """Create a parametric cylinder with variables"""
        
        position = position or {'x': 0, 'y': 0, 'z': 0}
        rotation = rotation or {'x': 0, 'y': 0, 'z': 0}
        
        # Create variables
        variables = {}
        radius = dimensions.get('radius', dimensions.get('diameter', 10) / 2)
        height = dimensions.get('height', 10)
        
        variables['radius'] = self.create_variable(
            f"{name}_radius", radius, 'mm', f'Radius of {name}'
        )
        variables['height'] = self.create_variable(
            f"{name}_height", height, 'mm', f'Height of {name}'
        )
        
        # Create position variables if not at origin
        if any(position.values()):
            variables['pos_x'] = self.create_variable(f"{name}_x", position['x'], 'mm', f'X position of {name}')
            variables['pos_y'] = self.create_variable(f"{name}_y", position['y'], 'mm', f'Y position of {name}')
            variables['pos_z'] = self.create_variable(f"{name}_z", position['z'], 'mm', f'Z position of {name}')
        
        # Create the cylinder object
        obj = self.doc.addObject("Part::Cylinder", name)
        
        # Set parametric expressions
        obj.setExpression('Radius', variables['radius'])
        obj.setExpression('Height', variables['height'])
        
        # Set position
        if any(position.values()):
            obj.setExpression('Placement.Base.x', variables['pos_x'])
            obj.setExpression('Placement.Base.y', variables['pos_y'])
            obj.setExpression('Placement.Base.z', variables['pos_z'])
        else:
            obj.Placement.Base = FreeCAD.Vector(0, 0, 0)
        
        # Set rotation if specified
        if any(rotation.values()):
            obj.Placement.Rotation = FreeCAD.Rotation(rotation['x'], rotation['y'], rotation['z'])
        
        return obj, variables
    
    def create_parametric_sphere(self, name: str, dimensions: Dict[str, float], 
                                position: Dict[str, float] = None, 
                                rotation: Dict[str, float] = None) -> Tuple[Any, Dict[str, str]]:
        """Create a parametric sphere with variables"""
        
        position = position or {'x': 0, 'y': 0, 'z': 0}
        rotation = rotation or {'x': 0, 'y': 0, 'z': 0}
        
        # Create variables
        variables = {}
        radius = dimensions.get('radius', dimensions.get('diameter', 10) / 2)
        
        variables['radius'] = self.create_variable(
            f"{name}_radius", radius, 'mm', f'Radius of {name}'
        )
        
        # Create position variables if not at origin
        if any(position.values()):
            variables['pos_x'] = self.create_variable(f"{name}_x", position['x'], 'mm', f'X position of {name}')
            variables['pos_y'] = self.create_variable(f"{name}_y", position['y'], 'mm', f'Y position of {name}')
            variables['pos_z'] = self.create_variable(f"{name}_z", position['z'], 'mm', f'Z position of {name}')
        
        # Create the sphere object
        obj = self.doc.addObject("Part::Sphere", name)
        
        # Set parametric expressions
        obj.setExpression('Radius', variables['radius'])
        
        # Set position
        if any(position.values()):
            obj.setExpression('Placement.Base.x', variables['pos_x'])
            obj.setExpression('Placement.Base.y', variables['pos_y'])
            obj.setExpression('Placement.Base.z', variables['pos_z'])
        else:
            obj.Placement.Base = FreeCAD.Vector(0, 0, 0)
        
        # Set rotation if specified
        if any(rotation.values()):
            obj.Placement.Rotation = FreeCAD.Rotation(rotation['x'], rotation['y'], rotation['z'])
        
        return obj, variables
    
    def create_parametric_cone(self, name: str, dimensions: Dict[str, float], 
                              position: Dict[str, float] = None, 
                              rotation: Dict[str, float] = None) -> Tuple[Any, Dict[str, str]]:
        """Create a parametric cone with variables"""
        
        position = position or {'x': 0, 'y': 0, 'z': 0}
        rotation = rotation or {'x': 0, 'y': 0, 'z': 0}
        
        # Create variables
        variables = {}
        radius1 = dimensions.get('radius', dimensions.get('diameter', 10) / 2)
        radius2 = dimensions.get('radius2', 0)
        height = dimensions.get('height', 10)
        
        variables['radius1'] = self.create_variable(
            f"{name}_radius1", radius1, 'mm', f'Base radius of {name}'
        )
        variables['radius2'] = self.create_variable(
            f"{name}_radius2", radius2, 'mm', f'Top radius of {name}'
        )
        variables['height'] = self.create_variable(
            f"{name}_height", height, 'mm', f'Height of {name}'
        )
        
        # Create position variables if not at origin
        if any(position.values()):
            variables['pos_x'] = self.create_variable(f"{name}_x", position['x'], 'mm', f'X position of {name}')
            variables['pos_y'] = self.create_variable(f"{name}_y", position['y'], 'mm', f'Y position of {name}')
            variables['pos_z'] = self.create_variable(f"{name}_z", position['z'], 'mm', f'Z position of {name}')
        
        # Create the cone object
        obj = self.doc.addObject("Part::Cone", name)
        
        # Set parametric expressions
        obj.setExpression('Radius1', variables['radius1'])
        obj.setExpression('Radius2', variables['radius2'])
        obj.setExpression('Height', variables['height'])
        
        # Set position
        if any(position.values()):
            obj.setExpression('Placement.Base.x', variables['pos_x'])
            obj.setExpression('Placement.Base.y', variables['pos_y'])
            obj.setExpression('Placement.Base.z', variables['pos_z'])
        else:
            obj.Placement.Base = FreeCAD.Vector(0, 0, 0)
        
        # Set rotation if specified
        if any(rotation.values()):
            obj.Placement.Rotation = FreeCAD.Rotation(rotation['x'], rotation['y'], rotation['z'])
        
        return obj, variables
    
    def create_parametric_torus(self, name: str, dimensions: Dict[str, float], 
                               position: Dict[str, float] = None, 
                               rotation: Dict[str, float] = None) -> Tuple[Any, Dict[str, str]]:
        """Create a parametric torus with variables"""
        
        position = position or {'x': 0, 'y': 0, 'z': 0}
        rotation = rotation or {'x': 0, 'y': 0, 'z': 0}
        
        # Create variables
        variables = {}
        radius1 = dimensions.get('major_radius', dimensions.get('radius', 20))
        radius2 = dimensions.get('minor_radius', dimensions.get('tube_radius', 5))
        
        variables['radius1'] = self.create_variable(
            f"{name}_major_radius", radius1, 'mm', f'Major radius of {name}'
        )
        variables['radius2'] = self.create_variable(
            f"{name}_minor_radius", radius2, 'mm', f'Minor radius of {name}'
        )
        
        # Create position variables if not at origin
        if any(position.values()):
            variables['pos_x'] = self.create_variable(f"{name}_x", position['x'], 'mm', f'X position of {name}')
            variables['pos_y'] = self.create_variable(f"{name}_y", position['y'], 'mm', f'Y position of {name}')
            variables['pos_z'] = self.create_variable(f"{name}_z", position['z'], 'mm', f'Z position of {name}')
        
        # Create the torus object
        obj = self.doc.addObject("Part::Torus", name)
        
        # Set parametric expressions
        obj.setExpression('Radius1', variables['radius1'])
        obj.setExpression('Radius2', variables['radius2'])
        
        # Set position
        if any(position.values()):
            obj.setExpression('Placement.Base.x', variables['pos_x'])
            obj.setExpression('Placement.Base.y', variables['pos_y'])
            obj.setExpression('Placement.Base.z', variables['pos_z'])
        else:
            obj.Placement.Base = FreeCAD.Vector(0, 0, 0)
        
        # Set rotation if specified
        if any(rotation.values()):
            obj.Placement.Rotation = FreeCAD.Rotation(rotation['x'], rotation['y'], rotation['z'])
        
        return obj, variables
    
    def create_parametric_wedge(self, name: str, dimensions: Dict[str, float], 
                               position: Dict[str, float] = None, 
                               rotation: Dict[str, float] = None) -> Tuple[Any, Dict[str, str]]:
        """Create a parametric wedge with variables"""
        
        position = position or {'x': 0, 'y': 0, 'z': 0}
        rotation = rotation or {'x': 0, 'y': 0, 'z': 0}
        
        # Create variables
        variables = {}
        length = dimensions.get('length', 10)
        width = dimensions.get('width', 10)
        height = dimensions.get('height', 10)
        
        variables['length'] = self.create_variable(
            f"{name}_length", length, 'mm', f'Length of {name}'
        )
        variables['width'] = self.create_variable(
            f"{name}_width", width, 'mm', f'Width of {name}'
        )
        variables['height'] = self.create_variable(
            f"{name}_height", height, 'mm', f'Height of {name}'
        )
        
        # Create position variables if not at origin
        if any(position.values()):
            variables['pos_x'] = self.create_variable(f"{name}_x", position['x'], 'mm', f'X position of {name}')
            variables['pos_y'] = self.create_variable(f"{name}_y", position['y'], 'mm', f'Y position of {name}')
            variables['pos_z'] = self.create_variable(f"{name}_z", position['z'], 'mm', f'Z position of {name}')
        
        # Create the wedge object
        obj = self.doc.addObject("Part::Wedge", name)
        
        # Set parametric expressions
        obj.setExpression('Xmax', variables['length'])
        obj.setExpression('Ymax', variables['width'])
        obj.setExpression('Zmax', variables['height'])
        
        # Set position
        if any(position.values()):
            obj.setExpression('Placement.Base.x', variables['pos_x'])
            obj.setExpression('Placement.Base.y', variables['pos_y'])
            obj.setExpression('Placement.Base.z', variables['pos_z'])
        else:
            obj.Placement.Base = FreeCAD.Vector(0, 0, 0)
        
        # Set rotation if specified
        if any(rotation.values()):
            obj.Placement.Rotation = FreeCAD.Rotation(rotation['x'], rotation['y'], rotation['z'])
        
        return obj, variables
    
    def create_parametric_hexagon(self, name: str, dimensions: Dict[str, float], 
                                 position: Dict[str, float] = None, 
                                 rotation: Dict[str, float] = None) -> Tuple[Any, Dict[str, str]]:
        """Create a parametric hexagon with variables"""
        
        position = position or {'x': 0, 'y': 0, 'z': 0}
        rotation = rotation or {'x': 0, 'y': 0, 'z': 0}
        
        # Create variables
        variables = {}
        width = dimensions.get('width', dimensions.get('diameter', dimensions.get('size', 20)))
        height = dimensions.get('height', 10)
        
        variables['width'] = self.create_variable(
            f"{name}_width", width, 'mm', f'Width of {name}'
        )
        variables['height'] = self.create_variable(
            f"{name}_height", height, 'mm', f'Height of {name}'
        )
        
        # Create position variables if not at origin
        if any(position.values()):
            variables['pos_x'] = self.create_variable(f"{name}_x", position['x'], 'mm', f'X position of {name}')
            variables['pos_y'] = self.create_variable(f"{name}_y", position['y'], 'mm', f'Y position of {name}')
            variables['pos_z'] = self.create_variable(f"{name}_z", position['z'], 'mm', f'Z position of {name}')
        
        # Create hexagon using Part workbench with expressions
        import Part
        import math
        
        # For parametric hexagon, we'll create a sketch-based approach or use a feature script
        # For now, let's create it as a Part::Feature with a parametric approach
        obj = self.doc.addObject("Part::Feature", name)
        
        # Create a function that will be called when parameters change
        def create_hexagon_shape():
            # Get current values from spreadsheet
            current_width = float(self.spreadsheet.get(f'B{self.variable_counter-2}'))  # width
            current_height = float(self.spreadsheet.get(f'B{self.variable_counter-1}'))  # height
            
            radius = current_width / 2
            points = []
            for i in range(6):
                angle = i * math.pi / 3
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                points.append(FreeCAD.Vector(x, y, 0))
            points.append(points[0])  # Close the polygon
            
            # Create wire from points
            edges = []
            for i in range(len(points)-1):
                edges.append(Part.makeLine(points[i], points[i+1]))
            wire = Part.Wire(edges)
            face = Part.Face(wire)
            
            # Extrude to create solid
            solid = face.extrude(FreeCAD.Vector(0, 0, current_height))
            return solid
        
        # Set initial shape
        obj.Shape = create_hexagon_shape()
        
        # Note: For full parametric behavior, we'd need to use expressions or feature scripts
        # This is a simplified version that creates the initial shape
        
        # Set position
        if any(position.values()):
            obj.setExpression('Placement.Base.x', variables['pos_x'])
            obj.setExpression('Placement.Base.y', variables['pos_y'])
            obj.setExpression('Placement.Base.z', variables['pos_z'])
        else:
            obj.Placement.Base = FreeCAD.Vector(0, 0, 0)
        
        # Set rotation if specified
        if any(rotation.values()):
            obj.Placement.Rotation = FreeCAD.Rotation(rotation['x'], rotation['y'], rotation['z'])
        
        return obj, variables
    
    def add_constraint(self, expression: str, description: str = '') -> str:
        """Add a constraint/calculated variable to the spreadsheet"""
        constraint_name = f"constraint_{self.variable_counter}"
        
        # Add to spreadsheet
        row = self.variable_counter
        self.spreadsheet.set(f'A{row}', constraint_name)
        self.spreadsheet.set(f'B{row}', f"={expression}")
        self.spreadsheet.set(f'C{row}', 'calculated')
        self.spreadsheet.set(f'D{row}', description)
        
        self.variable_counter += 1
        
        return f"{self.spreadsheet.Name}.{constraint_name}"
    
    def get_spreadsheet_reference(self) -> str:
        """Get reference to the parameters spreadsheet"""
        return self.spreadsheet.Name
    
    def list_variables(self) -> List[Dict[str, str]]:
        """List all variables in the spreadsheet"""
        variables = []
        if not hasattr(self.spreadsheet, 'getUsedCells'):
            return variables
        
        used_cells = self.spreadsheet.getUsedCells()
        for cell in used_cells:
            if cell.startswith('A') and cell != 'A1':
                try:
                    row = cell[1:]
                    name = self.spreadsheet.get(f'A{row}')
                    value = self.spreadsheet.get(f'B{row}')
                    unit = self.spreadsheet.get(f'C{row}')
                    desc = self.spreadsheet.get(f'D{row}')
                    
                    variables.append({
                        'name': name,
                        'value': value,
                        'unit': unit,
                        'description': desc,
                        'reference': f"{self.spreadsheet.Name}.{name}"
                    })
                except:
                    continue
        
        return variables