bl_info = {
    "name": "Action Keyframe Insertion",
    "author": "ffabian",
    "version": (1, 0),
    "blender": (3, 4, 0),
    "location": "AssetBrowser > Toolbar",
    "description": "Select an action from the asset browser and append its keyframes to an action in the Action Editor.",
    "warning": "",
    "wiki_url": "",
    "category": "Animation"
}


import bpy

from pathlib import Path

class InsertActionKeyframes(bpy.types.Operator):
    bl_idname = "asset.insert_action_keyframes"
    bl_label = "Insert Action Keyframes"

    @classmethod
    def poll(cls, context):
        return context.selected_asset_files

    def execute(self, context):

        current_library_name = context.area.spaces.active.params.asset_library_ref
        num_selected = len(context.selected_asset_files)
        
        if num_selected == 1:
            
            asset_file = context.selected_asset_files[0]        
            
            # Check if current asset file is an action
            if asset_file.id_type=="ACTION":
                
                #If asset belongs to external library and has not been linked before, link it
                if current_library_name != "LOCAL": 
                    is_linked_action = bpy.data.actions.get(asset_file.name)
                    if is_linked_action == None:                
                        library_path = Path(context.preferences.filepaths.asset_libraries.get(current_library_name).path)
                        library_to_load = str(library_path)+'/'+asset_file.relative_path.split('.')[0]+'.blend'            
                        with bpy.data.libraries.load(library_to_load, link=True, assets_only=True) as (data_from, data_to):
                            data_to.actions = data_from.actions
                    
                #Selected action from Asset Browser
                action = bpy.data.actions.get(asset_file.name)
                
                #Target action from Action Editor
                ob = bpy.context.object
                target_action = (ob.animation_data.action 
                    if ob.animation_data is not None
                    else None)
                    
                                
                #If valid, we will try to copy from Action to TargetAction
                if target_action != None:
                    
                    start_frame = bpy.context.scene.frame_current
                    print("About to copyframes to.. " + target_action.name + " at frame " + str(start_frame) )

                    for fcu in action.fcurves:                                                                                    
                        #If curve in Action exists in TargetAction
                        target_fcurve = target_action.fcurves.find(data_path=fcu.data_path, index=fcu.array_index)
                        if target_fcurve != None:
                            print("fcurve to paste: " + target_fcurve.data_path)                                                                                        
                            for keyframe in fcu.keyframe_points:                        
                                target_fcurve.keyframe_points.insert(start_frame + keyframe.co.x, keyframe.co.y)
                
                  
        
        #Updates dopesheet related UI
        for area in bpy.context.screen.areas:
            if area.type == 'DOPESHEET_EDITOR':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region.tag_redraw()
                    if region.type == 'CHANNELS':
                        region.tag_redraw()
                  
            #if current_library_name == "LOCAL":
            #    print(f"{asset_file.local_id.name} is selected in the asset browser. (Local File)")
            #else:
            #    asset_fullpath = library_path / asset_file.relative_path
            #    print(f"{asset_fullpath} is selected in the asset browser.")
            #    print(f"It is located in a user library named '{current_library_name}'")
            
        return {"FINISHED"}


def display_button(self, context):
    self.layout.operator(InsertActionKeyframes.bl_idname)


def register():
    bpy.utils.register_class(InsertActionKeyframes)
    bpy.types.ASSETBROWSER_MT_editor_menus.append(display_button)


def unregister():
    bpy.types.ASSETBROWSER_MT_editor_menus.remove(display_button)
    bpy.utils.unregister_class(InsertActionKeyframes)


if __name__ == "__main__":
    register()