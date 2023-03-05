import bpy

from pathlib import Path

class PrintSelectedAssets(bpy.types.Operator):
    bl_idname = "asset.print_selected_assets"
    bl_label = "Print Selected Assets"

    @classmethod
    def poll(cls, context):
        return context.selected_asset_files

    def execute(self, context):
        current_library_name = context.area.spaces.active.params.asset_library_ref
        if current_library_name != "LOCAL":  # NOT Current file
            library_path = Path(context.preferences.filepaths.asset_libraries.get(current_library_name).path)

        for asset_file in context.selected_asset_files:
            
            # Check if current asset file is an action
            if asset_file.id_type=="ACTION":                                            
                action = bpy.data.actions.get(asset_file.name)
                
                #Selected action in Action Editor
                ob = bpy.context.object
                target_action = (ob.animation_data.action 
                    if ob.animation_data is not None
                    else None)
                    
                                
                #If valid, we will try to copy from Action to TargetAction
                if target_action != None:
                    
                    start_frame = bpy.context.scene.frame_current
                    print("About to copyframes to.." + target_action.name + " at frame " + str(start_frame) )

                    for fcu in action.fcurves:                        
                                                                        
                        #print(fcu.data_path + " channel " + str(fcu.array_index))                        
                        #If curve in Action exists in TargetAction
                        target_fcurve = target_action.fcurves.find(data_path=fcu.data_path, index=fcu.array_index)
                        if target_fcurve != None:
                            print("fcurve to paste: " + target_fcurve.data_path)                                                                                        
                            for keyframe in fcu.keyframe_points:                        
                                #start_frame = start_frame + keyframe.co.x
                                target_fcurve.keyframe_points.insert(start_frame + keyframe.co.x, keyframe.co.y)
                                #print(keyframe.co) #coordinates x,y                            
                    
                    
                    #print("")
                    #print("current action data")
                    #for fcu in ob.animation_data.action.fcurves:
                    #    print(fcu.data_path + " channel " + str(fcu.array_index))
                    #    for keyframe in fcu.keyframe_points:
                    #        print(keyframe.co) #coordinates x,y
                        
                        
            #if current_library_name == "LOCAL":
            #    print(f"{asset_file.local_id.name} is selected in the asset browser. (Local File)")
            #else:
            #    asset_fullpath = library_path / asset_file.relative_path
            #    print(f"{asset_fullpath} is selected in the asset browser.")
            #    print(f"It is located in a user library named '{current_library_name}'")
            
        return {"FINISHED"}


def display_button(self, context):
    self.layout.operator(PrintSelectedAssets.bl_idname)


def register():
    bpy.utils.register_class(PrintSelectedAssets)
    bpy.types.ASSETBROWSER_MT_editor_menus.append(display_button)


def unregister():
    bpy.types.ASSETBROWSER_MT_editor_menus.remove(display_button)
    bpy.utils.unregister_class(PrintSelectedAssets)


if __name__ == "__main__":
    register()