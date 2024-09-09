import maya.cmds as cmds
import maya.mel as mel

def transfer_normals():
    # 获取选择的物体
    selection = cmds.ls(selection=True)
    
    if len(selection) != 2:
        cmds.warning("请选择两个物体：源模型和目标模型")
        return
    
    source_model = selection[0]
    target_model = selection[1]
    
    # 获取目标模型的蒙皮簇
    skin_cluster = mel.eval('findRelatedSkinCluster("{}")'.format(target_model))
    
    if skin_cluster:
        # 如果存在蒙皮簇,获取蒙皮信息并解绑
        joints = cmds.skinCluster(skin_cluster, query=True, influence=True)
        
        # 获取所有顶点
        vertices = cmds.ls("{}.vtx[*]".format(target_model), flatten=True)
        
        # 存储每个顶点的权重
        weights_per_vertex = []
        for vertex in vertices:
            weights = cmds.skinPercent(skin_cluster, vertex, query=True, value=True)
            weights_per_vertex.append(weights)
        
        cmds.skinCluster(skin_cluster, edit=True, unbind=True)
    
    # 传递法线
    cmds.transferAttributes(source_model, target_model, 
                            transferNormals=1, 
                            transferUVs=0, 
                            sampleSpace=0,  # 使用组件空间
                            searchMethod=3)
    
    if skin_cluster:
        # 重新绑定蒙皮并应用原来的权重
        new_skin_cluster = cmds.skinCluster(joints, target_model, tsb=True)[0]
        for i, vertex in enumerate(vertices):
            cmds.skinPercent(new_skin_cluster, vertex, transformValue=list(zip(joints, weights_per_vertex[i])))
    
    # 刷新法线显示
    cmds.polyNormalPerVertex(target_model, unFreezeNormal=True)
    cmds.polyNormalPerVertex(target_model, freezeNormal=True)
    
    # 选择目标模型并显示法线
    cmds.select(target_model)
    
    # 使用替代方法显示法线
    cmds.setAttr(target_model + ".displayNormal", 1)
    cmds.polyOptions(target_model, displayNormal=True)
    
    print("法线传递完成")

# 创建用户界面
def create_ui():
    window_name = "NormalTransferTool"
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
    
    window = cmds.window(window_name, title="法线传递工具", widthHeight=(200, 100))
    cmds.columnLayout(adjustableColumn=True)
    cmds.button(label="传递法线", command=lambda x: transfer_normals())
    cmds.showWindow(window)

create_ui()





