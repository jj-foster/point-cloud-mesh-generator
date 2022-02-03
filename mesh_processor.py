import open3d as o3d
import numpy as np
from PyQt5.QtWidgets import QMessageBox
import json

class Mesh():
    def __init__(self,mesh=None,pcd=None,psr_mesh=None):
        self.mesh=mesh
        self.pcd=pcd
        self.psr_mesh=psr_mesh
    
    def _import(self,file):
        self.mesh=o3d.io.read_triangle_mesh(file)
        self.mesh.compute_vertex_normals()

        return

    def pointsGen(self,window,points):
        try:
            self.points=int(points)
        except:
            QMessageBox.about(window,'Error','Only integer values accepted.')
            return

        self.pcd=self.mesh.sample_points_poisson_disk(self.points)

        return

    def pointsView(self):
        o3d.visualization.draw_geometries([self.pcd],point_show_normal=False,width=675,height=450)   

        return

    def generate(self):
        self.psr_mesh=o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
            self.pcd,
            depth=10,
            scale=2,
            linear_fit=False,
            n_threads=-1
            )[0]
        self.psr_mesh.paint_uniform_color(np.array([1,1,1]))

        return

    def smooth(self,window,iterations):
        if iterations!="":
            try:
                self.iterations=int(iterations)
                if self.iterations==0:
                    return
            except:
                QMessageBox.about(window,'Error','Only integer values accepted.')
                return

            self.psr_mesh=self.psr_mesh.filter_smooth_taubin(number_of_iterations=self.iterations)

        return

    def merge(self,window,distance):
        if distance!="":
            try:
                self.distance=int(distance)
                if self.distance==0:
                    return
            except:
                QMessageBox.about(window,'Error','Only integer values accepted.')
                return
                
            self.psr_mesh=self.psr_mesh.merge_close_vertices(self.distance)

        return

    def write(self,path):
        o3d.io.write_triangle_mesh(path,self.psr_mesh,write_vertex_normals=False,write_vertex_colors=False)
        
        return

    def display(self):
        o3d.visualization.draw_geometries([self.psr_mesh],mesh_show_wireframe=True,width=675,height=450)

        return