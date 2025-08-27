# VibeDesign Parametric Features 🎯

VibeDesign now creates **fully parametric objects** with variables and constraints, making your CAD workflow more powerful and flexible!

## ✨ What's New

### 🔧 **Parametric Objects by Default**
- All objects are now created with **variables** instead of fixed values
- Each dimension becomes a **named parameter** stored in a spreadsheet
- **Easy modification** through the parameters spreadsheet
- **Automatic recalculation** when parameters change

### 📊 **Integrated Spreadsheet Management**
- **VibeDesign Parameters** spreadsheet automatically created
- **Organized variables** with descriptions and units
- **Constraint support** for relationships between objects
- **Visual parameter management** through FreeCAD's spreadsheet editor

## 🎮 **How to Use**

### 1. **Toggle Parametric Mode**
```
Processing Mode: ☑ Use AI Agent
Object Creation: ☑ Create Parametric Objects  ← New toggle!
```

### 2. **Create Objects (Same Commands)**
```
create a box 20x15x10 mm
make a cylinder radius 8 height 25
create a sphere diameter 16 cm
```

### 3. **View Results**
**Before (Fixed Values):**
```
✓ Created: Box (20.0 x 15.0 x 10.0 mm)
```

**Now (Parametric):**
```
✓ Created: Parametric Box (20.0 x 15.0 x 10.0 mm) [Variables: length=Box_length, width=Box_width, height=Box_height]
```

### 4. **Manage Parameters**
- Click **"View Parameters"** button to open spreadsheet
- **Edit values directly** in the spreadsheet
- **Watch objects update** in real-time!

## 🏗️ **Architecture**

### **ParametricObjectManager Class**
```python
# Creates objects with expressions instead of fixed values
obj.setExpression('Length', 'VibeDesign_Params.box_length')
obj.setExpression('Width', 'VibeDesign_Params.box_width')
```

### **Variable Naming Convention**
```
{object_name}_{parameter}
Examples:
- Box001_length
- Cylinder002_radius
- Sphere003_radius
```

### **Spreadsheet Structure**
| Variable | Value | Unit | Description |
|----------|-------|------|-------------|
| Box001_length | 20 | mm | Length of Box001 |
| Box001_width | 15 | mm | Width of Box001 |
| Box001_height | 10 | mm | Height of Box001 |

## 🔗 **Advanced Features**

### **Constraints & Relationships**
```python
# Create relationships between objects
pm.add_constraint("Box001_length * 2", "Double the box length")
pm.add_constraint("Cylinder001_radius + 5", "Cylinder radius plus 5mm")
```

### **Position Parameters**
Objects positioned away from origin get position variables:
```python
# Position variables automatically created
Box001_x = 10    # X position
Box001_y = 20    # Y position  
Box001_z = 0     # Z position
```

### **Unique Variable Names**
The system ensures no conflicts:
```
Box001_length, Box002_length, Box003_length...
```

## 🎯 **Benefits for CAD Design**

### **🔄 Easy Modifications**
- Change one parameter → all related geometry updates
- No need to recreate objects from scratch
- **Design intent preserved**

### **📐 Design Relationships** 
- Link dimensions between different objects
- Create **adaptive designs** that scale together
- **Mathematical relationships** between parameters

### **🎛️ Design Variants**
- Quickly create **multiple versions** by changing parameters
- **Family of parts** with different sizes
- **Parametric design studies**

### **📊 Design Documentation**
- **Self-documenting** designs with parameter descriptions
- **Clear intent** through named variables
- **Organized parameter management**

## 🖥️ **User Interface**

### **New Controls**
- **"Create Parametric Objects"** checkbox (enabled by default)
- **"View Parameters"** button opens spreadsheet editor
- **Real-time feedback** showing created variables

### **Enhanced Output**
Objects now show their parametric nature:
```
✓ Created: Parametric Cylinder (radius 8.0 mm, height 25.0 mm) 
  [Variables: radius=Cylinder001_radius, height=Cylinder001_height]
```

## 🔧 **Technical Implementation**

### **Expression-Based Objects**
Instead of:
```python
obj.Length = 20  # Fixed value
```

Now uses:
```python
obj.setExpression('Length', 'VibeDesign_Params.Box001_length')  # Parametric
```

### **Spreadsheet Integration**
- Automatic spreadsheet creation and management
- Variable name sanitization and uniqueness
- Organized layout with headers and descriptions

### **Backward Compatibility**
- Can toggle parametric mode off for simple objects
- Fallback to traditional fixed-value objects
- No breaking changes to existing workflows

## 🚀 **Examples**

### **Basic Parametric Box**
```
Input: "create a box 30x20x10 mm"
Creates: Parametric box with variables
Variables: Box001_length=30, Box001_width=20, Box001_height=10
```

### **Parametric Assembly**
```
1. "create a base plate 100x80x5 mm"
2. "create a cylinder on top radius 15 height 30"
3. Add constraint: base_length = cylinder_height + 70
```

### **Design Variants**
```
Change base_length from 100 to 150
→ All related dimensions update automatically
→ Assembly maintains design intent
```

## 💡 **Pro Tips**

1. **Use the spreadsheet editor** for bulk parameter changes
2. **Add descriptive comments** in the Description column
3. **Create constraints** for design relationships
4. **Group related parameters** by naming convention
5. **Use the toggle** to switch between parametric and simple modes

## 🔍 **Testing**

Run the test script in FreeCAD:
```python
# In FreeCAD Python console
exec(open('test_parametric.py').read())
```

This creates sample parametric objects and demonstrates all features!

---

**🎉 Happy Parametric Designing with VibeDesign!**

*Now your CAD objects are truly intelligent and adaptable!* 🚀