import numpy as np
import matplotlib.pyplot as plt
import timeit

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm

class Object:
    def __init__(self, position):
        self.position = position


class Ball(Object):
    def __init__(self,  position, radius, name):
        super().__init__( position)
        self.radius = radius
        self.name = name

class Plane(Object):
    def __init__(self, position, normal, name):
        super().__init__( position)
        self.normal = normal
        self.name = name


class Light:
    def __init__(self, position, intesity, name):
            self.position = position
            self.intesity = intesity
            self.name = name


#parameters
image_size = [500,500]
camera_position = np.array((0,-4,2))
fov = 90 *np.pi/180
render_distance = 10
epsilon = 0.00001
filter_size = 0.077

#ball
ball_position = np.array((0,0,1))
ball_radius = 1

b1 = Ball(ball_position, ball_radius, "b1")

#light
light_position = np.array((1.7,-1.7,2))
light_intesity = 1

l1 = Light(light_position,light_intesity, "l1")

def light_line(n):
    """
    For testing. Gives you a list of n lights in a line
    """
    temp_list = []
    for i in range(n):
        temp_list.append(Light(light_position + 120/n*i*np.array([0,1,0]),1, f"light line{i}"))

    return np.array(temp_list)

#plane
plane_position = np.array((0,0,0))
plane_normal = np.array((0,0,1))

p1 = Plane(plane_position, plane_normal, "p1")
p2 = Plane(np.array([-1.5,0,0]), np.array([1,0,0]), "p2")



objects_list = np.array([b1,p1,p2])
lights_list = np.array([l1])
# lights_list = light_line(20)

def collision(pos, dir, list):
    d0 = np.inf
    obj_id = 0
    normal = np.array([0,0,0])
    for el in list:
        d = np.inf
        if type(el) == Ball:
            b = np.dot(dir, pos-el.position)
            c = np.linalg.norm(pos-el.position)**2-el.radius**2
            dis = b**2 - c
            if dis >= 0:
                d = -b - np.sqrt(dis)
                if d < 0: d += 2 * np.sqrt(dis)
                if d < 0: d = np.inf
            
            if d < d0:
                d0 = d
                obj_id = id(el)
                normal = (pos + d0*dir - el.position)/el.radius
        
        elif type(el) == Plane:
            proj = np.dot(dir,el.normal)
            if proj != 0:
                d = np.dot((el.position - pos), el.normal)/proj
                if d > 0:
                    if d < d0:
                        d0 = d
                        obj_id = id(el)
                        normal = el.normal * (-1)* np.sign(proj)

    return pos + d0*dir, d0, obj_id, normal


def render(image_size, objects_list, lights_list):
    stage1 = {}
    image = np.zeros(image_size)
    phi = np.linspace(-fov/2,fov/2,image_size[0])
    for i in range(image_size[0]):
        for j in range(image_size[1]):
            direction = np.array((np.sin(phi[i]),1,np.sin(phi[j])))
            direction = normalize(direction)

            point, d1, object_id, nor = collision(camera_position, direction, objects_list)

            for el in lights_list:
                direction2 = el.position - point
                d = np.linalg.norm(direction2)
                direction2 /= d
                _, x, __, ___ = collision(point + epsilon*direction2, direction2, objects_list)

                if x > d and d1 < render_distance:
                    image[i,j] += 1/(d**2)*el.intesity * np.dot(nor, direction2)



            if image[i,j] != 0:
                power = image[i,j]*6*1/(image_size[0]*image_size[1])
                if object_id not in stage1.keys():
                    stage1[object_id] = [Light(point,power, object_id)]
                else:
                    stage1[object_id].append(Light(point,power, object_id))
    return image, stage1


def render2(image_size, objects_list, lights_list, ilumination_map):
    image = np.zeros(image_size)
    phi = np.linspace(-fov/2,fov/2,image_size[0])
    samp_s = fov/image_size[0]
    for i in range(image_size[0]):
            for j in range(image_size[1]):
                direction = np.array((np.sin(phi[i]),1,np.sin(phi[j])))
                direction = normalize(direction)
    
                point, d1 , object_id, nor = collision(camera_position, direction, objects_list)

                if d1 < render_distance:
                    for obj_key in ilumination_map:
                        if  obj_key != object_id:
                            for el in ilumination_map[obj_key]:
                                direction2 = el.position - point
                                d = np.linalg.norm(direction2)
                                direction2 /= d
                                _, x, col_id, nor1 = collision(point + epsilon*direction2, direction2, objects_list)
                                if col_id == obj_key:
                                    image[i,j] += 1/(d**2 + (samp_s*d1)**2) * el.intesity * np.dot(nor, direction2) * (-1)*np.dot(nor1, direction2)

                    for el in lights_list:
                        direction2 = el.position - point
                        d = np.linalg.norm(direction2)
                        direction2 /= d
                        _, x, __, ___ = collision(point + epsilon*direction2, direction2, objects_list)
                        if x > d and d1 < render_distance:
                            image[i,j] += 1/(d**2)*el.intesity * np.dot(nor, direction2)
    return image


t1 = timeit.default_timer()
image_dark_sh, stage1 = render((30,30), objects_list, lights_list)
t2 = timeit.default_timer()
print(f"first stage {t2-t1} s")

image_dark_sh = np.rot90(image_dark_sh,1)
plt.imshow(image_dark_sh,cmap='gray')
plt.axis('off')
plt.savefig("renders/image_dark_sh.png")

t1 = timeit.default_timer()
image = render2((500,500), objects_list, lights_list, stage1)
t2 = timeit.default_timer()
print(f"second stage {t2-t1} s")

image = np.rot90(image,1)
plt.imshow(image,cmap='gray')
plt.axis('off')
plt.savefig("renders/image.png")
image = np.rot90(image,-1)



def execute(preresolution, resolution, save=True):
    image_size = [preresolution,preresolution]
    image = np.zeros(image_size)

    t1 = timeit.default_timer()
    render()
    t2 = timeit.default_timer()
    print(f"first stage {t2-t1} s")

    

    if save:
        image_dark_sh = np.rot90(image_dark_sh,1)
        plt.imshow(image_dark_sh,cmap='gray')
        plt.axis('off')
        plt.savefig("renders/image_dark_sh.png")


    image0 = image.copy()

    image_size = [resolution,resolution]
    image = np.zeros(image_size)
    t1 = timeit.default_timer()
    render2()
    t2 = timeit.default_timer()
    print(f"{t2-t1} s")

    image += image0

    image = np.rot90(image,1)
    plt.imshow(image,cmap='gray')
    plt.axis('off')
    plt.show()

image = np.rot90(image,1)
plt.imshow(image,cmap='gray')
plt.axis('off')
plt.show()

# image = np.zeros(image_size)
# stage1.append(l1)
# phi = np.linspace(-fov/2,fov/2,image_size[0])
# for i in range(image_size[0]):
#     for j in range(image_size[1]):
#         direction = np.array((np.sin(phi[i]),1,np.sin(phi[j])))
#         direction = normalize(direction)

#         point, d1 = collision(camera_position, direction, objects_list)

#         for el in stage1:
#             d = np.linalg.norm(el.position - point)
#             direction2 = el.position - point
#             direction2 = normalize(direction2)
#             _, x = collision(point + epsilon*direction2, direction2, objects_list)

#             if x > d and d1 < render_distance:
#                 image[i,j] += 1/(d**2)*el.intesity


# phi = np.linspace(-fov/2,fov/2,image_size[0])
# for i in range(image_size[0]):
#     for j in range(image_size[1]):
#         direction = np.array((np.sin(phi[i]),1,np.sin(phi[j])))
#         direction = normalize(direction)

#         b = np.dot(direction,camera_position-ball_position)
#         c = np.linalg.norm(camera_position-ball_position)**2-ball_radius**2
                
#         if np.dot(direction,plane_normal) != 0:
#             d = np.dot((plane_position - camera_position),plane_normal)/np.dot(direction,plane_normal)
#             if d < render_distance:
#                 point = camera_position + d*direction
#                 image[i,j] = 1/(np.linalg.norm(point-light_position)**2)*light_intesity

#         if (b**2 - c) >= 0:
#             d = -b - np.sqrt(b**2 - c)
#             if d < 0: d = -b + np.sqrt(b**2 - c)
#             point = camera_position + d*direction

#             image[i,j] = 1/(np.linalg.norm(point-light_position)**2)*light_intesity






"""
print("5 - 50")

image_size = [5,5]
image = np.zeros(image_size)
t1 = timeit.default_timer()
render()
t2 = timeit.default_timer()
print(f"{t2-t1} s")

image_size = [50,50]
image = np.zeros(image_size)
t1 = timeit.default_timer()
render2()
t2 = timeit.default_timer()
print(f"{t2-t1} s")

image = np.rot90(image,1)
plt.imshow(image,cmap='gray')
plt.axis('off')
plt.savefig("renders/5-50.png")
image = np.rot90(image,-1)






print("10 - 50")

image_size = [10,10]
image = np.zeros(image_size)
t1 = timeit.default_timer()
render()
t2 = timeit.default_timer()
print(f"{t2-t1} s")

image_size = [50,50]
image = np.zeros(image_size)
t1 = timeit.default_timer()
render2()
t2 = timeit.default_timer()
print(f"{t2-t1} s")

image = np.rot90(image,1)
plt.imshow(image,cmap='gray')
plt.axis('off')
plt.savefig("renders/10-50.png")
image = np.rot90(image,-1)





print("20 - 50")

image_size = [20,20]
image = np.zeros(image_size)
t1 = timeit.default_timer()
render()
t2 = timeit.default_timer()
print(f"{t2-t1} s")

image_size = [50,50]
image = np.zeros(image_size)
t1 = timeit.default_timer()
render2()
t2 = timeit.default_timer()
print(f"{t2-t1} s")

image = np.rot90(image,1)
plt.imshow(image,cmap='gray')
plt.axis('off')
plt.savefig("renders/20-50.png")
image = np.rot90(image,-1)





print("50 - 50")

image_size = [50,50]
image = np.zeros(image_size)
t1 = timeit.default_timer()
render()
t2 = timeit.default_timer()
print(f"{t2-t1} s")

image_size = [50,50]
image = np.zeros(image_size)
t1 = timeit.default_timer()
render2()
t2 = timeit.default_timer()
print(f"{t2-t1} s")

image = np.rot90(image,1)
plt.imshow(image,cmap='gray')
plt.axis('off')
plt.savefig("renders/50-50.png")
image = np.rot90(image,-1)

"""